import os

# Required by bot.constants._Client (env_prefix="client_", field token). Set before any bot import.
os.environ.setdefault("CLIENT_TOKEN", "test-dummy-token-for-pytest")
