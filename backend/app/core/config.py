import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SCR Scheduler"
    API_V1_STR: str = "/api"

    # Si existe SQLALCHEMY_DATABASE_URI en env, úsalo.
    # Si no existe, lo construimos desde DB_HOST/DB_USER/DB_PASSWORD/DB_NAME/DB_PORT.
    # Si tampoco existen, caemos al default local (localhost).
    SQLALCHEMY_DATABASE_URI: str | None = None

    # Local fallback (para desarrollo)
    LOCAL_DB_URI: str = "mysql+pymysql://autospot:Mliriano@localhost:3306/supercarros_republisher?charset=utf8mb4"

    # JWT
    SECRET_KEY: str = "CHANGE_THIS_SECRET_IN_PRODUCTION"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 día

    # Credenciales de SuperCarros (variables de entorno)
    SUPERCARROS_USER: str = "SC_USER"
    SUPERCARROS_PASS: str = "SC_PASS"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def db_uri(self) -> str:
        # 1) Si viene completo por env, gana.
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI

        # 2) Si vienen piezas por env (como tu Flask test), construimos.
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        name = os.getenv("DB_NAME")
        port = os.getenv("DB_PORT", "3306")

        if host and user and password and name:
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"

        # 3) Fallback local.
        return self.LOCAL_DB_URI


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
