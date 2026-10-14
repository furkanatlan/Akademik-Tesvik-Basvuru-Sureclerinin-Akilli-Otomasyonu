from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    scholar_provider: str = "mock"  # mock | playwright | serpapi
    serpapi_key: str = ""
    contact_email: str = ""
    elsevier_api_key: str = ""

    scrape_min_delay_sec: float = 4
    scrape_max_delay_sec: float = 9
    cache_ttl_hours: int = 72

    database_url: str = "postgresql+psycopg://tesvik:tesvik@db:5432/tesvik"
    redis_url: str = "redis://redis:6379/0"
    data_dir: Path = Path("/data")
    grobid_url: str = "http://grobid:8070"

    # Paylaşımlı tarayıcı (WoS / Scopus kurum girişi)
    browser_cdp_host: str = "browser"
    browser_cdp_port: int = 9223
    novnc_public_url: str = "http://localhost:6080"
    # true: WoS veya Scopus girişi doğrulanmadan yayın/atıf taraması ve kanıt üretimi başlamaz
    require_db_login: bool = True
    db_session_ttl_hours: int = 8


@lru_cache
def get_settings() -> Settings:
    return Settings()
