"""Application configuration loading."""

from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from diamond_rca.paths import EXTERNAL_DATA_DIR


class AppConfig(BaseSettings):
    """Config values loaded from environment variables or defaults."""

    pythonpath: str = Field(default="src", alias="PYTHONPATH")
    cache_dir: str = Field(default=str(EXTERNAL_DATA_DIR / "cache"), alias="CACHE_DIR")
    default_team: str = Field(default="NYM", alias="DEFAULT_TEAM")
    default_season: int = Field(default=2025, alias="DEFAULT_SEASON")

    model_config = SettingsConfigDict(populate_by_name=True, extra="ignore")


def load_config(env_file: str | Path = ".env") -> AppConfig:
    """Load environment variables and return validated application config."""
    load_dotenv(env_file)
    return AppConfig()
