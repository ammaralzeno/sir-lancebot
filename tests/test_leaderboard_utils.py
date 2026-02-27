"""Unit tests for bot.utils.leaderboard (add_points, remove_points, get_leaderboard, etc.)."""
from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.utils.leaderboard import (
    DAILY_POINT_CAP,
    _get_points_cache,
    add_points,
    get_daily_leaderboard,
    get_leaderboard,
    get_user_points,
    get_user_rank,
    remove_points,
)


# --- Test doubles (no real Redis / Discord) ---


class FakePointsCache:
    """In-memory fake for RedisCache used by leaderboard utils."""

    def __init__(self) -> None:
        self._data: dict[int, int] = {}

    async def contains(self, user_id: int) -> bool:
        return user_id in self._data

    async def set(self, user_id: int, value: int) -> None:
        self._data[user_id] = value

    async def get(self, user_id: int) -> str | None:
        v = self._data.get(user_id)
        return str(v) if v is not None else None

    async def increment(self, user_id: int, delta: int) -> None:
        self._data[user_id] = self._data.get(user_id, 0) + delta

    async def decrement(self, user_id: int, delta: int) -> None:
        self._data[user_id] = max(0, self._data.get(user_id, 0) - delta)

    async def items(self) -> list[tuple[int, str]]:
        return [(uid, str(score)) for uid, score in self._data.items()]


class FakeRedis:
    """In-memory fake for redis_session.client (daily cap keys)."""

    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self._data.get(key)

    async def set(self, key: str, value: str | int, ex: int | None = None) -> None:
        self._data[key] = str(value)

    async def scan_iter(self, match: str):
        prefix = match.rstrip("*")
        for key in self._data:
            if key.startswith(prefix):
                yield key


class LeaderboardUtilsTests(unittest.IsolatedAsyncioTestCase):
    """ async tests for leaderboard utilities."""

    async def asyncSetUp(self) -> None:
        self.fake_points_cache = FakePointsCache()
        self.fake_redis = FakeRedis()

        self.mock_bot = MagicMock()
        self.mock_bot.redis_session = MagicMock()
        self.mock_bot.redis_session.client = self.fake_redis
        self.mock_bot.get_cog = MagicMock(return_value=MagicMock())

    # --- Internal helpers / wiring ---

    async def test_get_points_cache_uses_leaderboard_points_cache(self):
        """_get_points_cache returns Leaderboard.points_cache (integration with cog)."""
        with patch(
            "bot.exts.fun.leaderboard.Leaderboard.points_cache",
            self.fake_points_cache,
        ):
            cache = await _get_points_cache()
        self.assertIs(cache, self.fake_points_cache)

    # --- Points can be added ---

    async def test_add_points_increases_score(self):
        """add_points increases the user's stored total. Assert: return and cache match."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            with patch(
                "bot.utils.leaderboard.seconds_until_midnight_utc",
                return_value=3600,
            ):
                result = await add_points(self.mock_bot, 1001, 50, "test_game")
        self.assertEqual(result, 50)
        self.assertEqual(await self.fake_points_cache.get(1001), "50")

    async def test_add_points_increments_when_user_already_in_cache(self):
        """When user already has a score, add_points uses increment """
        await self.fake_points_cache.set(1002, 30)
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            with patch(
                "bot.utils.leaderboard.seconds_until_midnight_utc",
                return_value=3600,
            ):
                result = await add_points(self.mock_bot, 1002, 20, "test_game")
        self.assertEqual(result, 50)
        self.assertEqual(await self.fake_points_cache.get(1002), "50")

    async def test_add_points_zero_is_no_op(self):
        """Edge case: adding 0 points does not change score; returns current total (no write)."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            await self.fake_points_cache.set(1003, 10)
            result = await add_points(self.mock_bot, 1003, 0, "test_game")
        self.assertEqual(result, 10)

    async def test_add_points_returns_zero_when_cog_missing(self):
        """If Leaderboard cog is missing, add_points returns 0 and skips side effects."""
        self.mock_bot.get_cog.return_value = None
        result = await add_points(self.mock_bot, 42, 10, "any_game")
        self.assertEqual(result, 0)

    async def test_add_points_daily_cap_no_add(self):
        """Daily cap hit: no new points added, returns current global total unchanged."""
        await self.fake_redis.set("leaderboard:daily:99:g", str(DAILY_POINT_CAP))  
        with patch("bot.utils.leaderboard._get_points_cache", AsyncMock(return_value=self.fake_points_cache)):
            await self.fake_points_cache.set(99, 50)  
            result = await add_points(self.mock_bot, 99, 10, "g")
        self.assertEqual(result, 50)  

    # --- Points can be removed ---

    async def test_remove_points_decreases_score(self):
        """remove_points decreases the user's stored total. Assert: new total = old - removed."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            await self.fake_points_cache.set(2001, 100)
            result = await remove_points(self.mock_bot, 2001, 30)
        self.assertEqual(result, 70)
        self.assertEqual(await self.fake_points_cache.get(2001), "70")

    async def test_remove_points_zero_or_negative_returns_current(self):
        """Edge case: remove_points with amount <= 0 returns current score; no change."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            await self.fake_points_cache.set(2003, 40)
            r1 = await remove_points(self.mock_bot, 2003, 0)
            r2 = await remove_points(self.mock_bot, 2003, -5)
        self.assertEqual(r1, 40)
        self.assertEqual(r2, 40)
        self.assertEqual(await self.fake_points_cache.get(2003), "40")

    async def test_remove_points_returns_zero_when_user_missing(self):
        """Removing points for a user without stored score returns 0."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            result = await remove_points(self.mock_bot, 9999, 10)
        self.assertEqual(result, 0)

    # --- get_user_points / leaderboard read ---

    async def test_get_user_points_returns_zero_when_no_cog(self):
        """When Leaderboard cog is not loaded, get_user_points returns 0 (no crash)."""
        self.mock_bot.get_cog.return_value = None
        result = await get_user_points(self.mock_bot, 9999)
        self.assertEqual(result, 0)

    # --- Leaderboard view (ranked list) ---

    async def test_get_leaderboard_returns_empty_when_cog_missing(self):
        """When Leaderboard cog is not loaded, get_leaderboard returns empty list."""
        self.mock_bot.get_cog.return_value = None
        result = await get_leaderboard(self.mock_bot)
        self.assertEqual(result, [])

    # --- get_user_rank ---

    async def test_get_user_rank_returns_rank_when_on_leaderboard(self):
        """get_user_rank returns 1-based position when user is on the leaderboard."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            await self.fake_points_cache.set(7001, 100)
            await self.fake_points_cache.set(7002, 200)
            await self.fake_points_cache.set(7003, 50)
            self.assertEqual(await get_user_rank(self.mock_bot, 7002), 1)
            self.assertEqual(await get_user_rank(self.mock_bot, 7001), 2)
            self.assertEqual(await get_user_rank(self.mock_bot, 7003), 3)

    async def test_get_user_rank_returns_none_when_not_on_leaderboard(self):
        """get_user_rank returns None when user has no score or zero score."""
        with patch(
            "bot.utils.leaderboard._get_points_cache",
            AsyncMock(return_value=self.fake_points_cache),
        ):
            await self.fake_points_cache.set(7004, 10)
            self.assertIsNone(await get_user_rank(self.mock_bot, 9999))
            await self.fake_points_cache.set(7005, 0)
            self.assertIsNone(await get_user_rank(self.mock_bot, 7005))

    # --- get_daily_leaderboard ---

    async def test_get_daily_leaderboard_returns_empty_when_cog_missing(self):
        """When Leaderboard cog is not loaded, get_daily_leaderboard returns empty list."""
        self.mock_bot.get_cog.return_value = None
        result = await get_daily_leaderboard(self.mock_bot)
        self.assertEqual(result, [])

    async def test_get_daily_leaderboard_skips_malformed_keys(self):
        """Keys that do not have exactly 4 parts (prefix:user_id:game) are skipped."""
        await self.fake_redis.set("leaderboard:daily:9001:ok", "10")
        await self.fake_redis.set("leaderboard:daily:bad:key:extra", "5")
        result = await get_daily_leaderboard(self.mock_bot)
        self.assertEqual(result, [(9001, 10)])

