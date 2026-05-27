import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Settings:
    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'dev-only-change-me')
    DEBUG: bool = os.environ.get('DEBUG', 'false').lower() == 'true'
    DB_PATH: str = os.environ.get('DB_PATH', str(Path(__file__).resolve().parent.parent / 'tasks.db'))
    HOST: str = os.environ.get('HOST', '0.0.0.0')
    PORT: int = int(os.environ.get('PORT', '5000'))
    SMTP_HOST: str = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.environ.get('SMTP_PORT', '587'))
    SMTP_USER: str = os.environ.get('SMTP_USER', '')
    SMTP_PASSWORD: str = os.environ.get('SMTP_PASSWORD', '')


settings = Settings()
