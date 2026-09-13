from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://twistfit:twistfit@localhost:5432/twistfit_dev"
    jwt_secret: str = "dev-only-insecure-jwt-secret"
    cors_origins: str = "http://localhost:3000"
    cookie_domain: str | None = None
    cookie_secure: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
