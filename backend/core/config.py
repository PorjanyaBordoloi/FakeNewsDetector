"""
core/config.py — Centralised settings via pydantic_settings.

Reads from the .env file at project root.
All services import `settings` from here — no os.getenv() scattered around.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve project root: backend/core/config.py -> backend/ -> project root
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    NEWS_API: str = ""

    model_config = {
        "env_file": str(_ENV_FILE),
        "env_file_encoding": "utf-8",
    }


# Singleton — import this everywhere
settings = Settings()
