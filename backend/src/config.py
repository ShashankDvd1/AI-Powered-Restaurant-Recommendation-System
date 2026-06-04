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

    # Generic/configurable LLM properties
    llm_api_key: str = ""
    llm_api_base: str = "https://api.groq.com/openai/v1"
    llm_model: str = "llama-3.3-70b-versatile"

    # Groq settings
    groq_api_key: str = ""
    groq_model: str = ""

    # Backward compatibility settings
    xai_api_key: str = ""
    grok_model: str = "grok-2-latest"
    
    cors_origins: str = "http://localhost:3000"
    data_path: str = ""

    @property
    def active_llm_key(self) -> str:
        # Prioritize LLM_API_KEY, then GROQ_API_KEY, and fallback to XAI_API_KEY
        return (
            self.llm_api_key
            or self.groq_api_key
            or self.xai_api_key
            or ""
        )

    @property
    def active_llm_base(self) -> str:
        # Fallback to xAI console base url if ONLY XAI_API_KEY is present
        if not self.llm_api_key and not self.groq_api_key and self.xai_api_key:
            return "https://api.x.ai/v1"
        return self.llm_api_base

    @property
    def active_llm_model(self) -> str:
        # Fallback to grok model name if ONLY XAI_API_KEY is present
        if not self.llm_api_key and not self.groq_api_key and self.xai_api_key:
            return self.grok_model
        return self.groq_model or self.llm_model

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
