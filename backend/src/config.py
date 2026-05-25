from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ directory
BACKEND_DIR = Path(__file__).resolve().parents[1]
# repository root
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "restaurants.parquet"
INGESTION_REPORT_PATH = PROJECT_ROOT / "data" / "ingestion_report.txt"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    xai_api_key: str = ""
    grok_model: str = "grok-2-latest"
    cors_origins: str = "http://localhost:3000"
    data_path: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def processed_data_path(self) -> Path:
        if self.data_path:
            return Path(self.data_path)
        return DEFAULT_DATA_PATH


@lru_cache
def get_settings() -> Settings:
    return Settings()
