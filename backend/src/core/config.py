from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql://postgres:basepg123@localhost:5432/boletoya_db"
    JWT_SECRET_KEY: str = "secret-boletoya-super-secure-key-change-in-prod-2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:5173"

    # Password recovery
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # SMTP (Mailtrap Email Sandbox during testing). No real credentials as defaults.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 2525
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    MAIL_FROM_ADDRESS: str = "no-reply@boletoya.local"
    MAIL_FROM_NAME: str = "BoletoYa"


settings = Settings()
