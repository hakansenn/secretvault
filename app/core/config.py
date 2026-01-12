from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    app_name: str = "SecureVault"
    env: str = "dev"

    jwt_secret: str
    database_url: str

    access_token_minutes: int = 60
    upload_dir: str = "uploads"
    max_upload_mb: int = 10


settings = Settings()