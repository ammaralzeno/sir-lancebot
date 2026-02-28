"""Scoring rule tests: when a game awards points, the correct call to leaderboard utils is made"""
from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from bot.exts.fun.coinflip import COINFLIP_WIN_POINTS, CoinFlip


class ScoringRulesTests(unittest.IsolatedAsyncioTestCase):
    """ async tests for scoring rules """

    # --- Coinflip ---

    async def test_coinflip_win_calls_add_points_with_correct_value(self):
        """When user wins coinflip, add_points is called with correct points and game name."""
        mock_bot = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.author.id = 12345
        mock_ctx.send = AsyncMock()

        with patch("bot.exts.fun.coinflip.add_points", new_callable=AsyncMock) as mock_add_points:
            with patch("bot.exts.fun.coinflip.random.choice", return_value="heads"):
                cog = CoinFlip(mock_bot)
                await cog.coinflip_command.callback(cog, mock_ctx, "heads")

        mock_add_points.assert_called_once_with(
            mock_bot,
            12345,
            COINFLIP_WIN_POINTS,
            "coinflip",
        )
        self.assertEqual(COINFLIP_WIN_POINTS, 2)
