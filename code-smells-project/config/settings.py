import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
    DB_PATH: str = os.environ.get(
        "DB_PATH",
        str(Path(__file__).resolve().parent.parent / "loja.db"),
    )
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", "5000"))
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")


settings = Settings()
