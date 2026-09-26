from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://twistfit:twistfit@localhost:5432/twistfit_dev"
    jwt_secret: str = "dev-only-insecure-jwt-secret"
    cors_origins: str = "http://localhost:3000"
    cookie_domain: str | None = None
    cookie_secure: bool = False
    gemini_api_key: str = "dev-only-placeholder-gemini-key"
    flux_api_base_url: str = "https://api.bfl.ai"
    flux_api_key: str = "dev-only-placeholder-flux-api-key"
    frontend_base_url: str = "http://localhost:3000"

    # minio_endpoint is what the backend container uses to talk to MinIO
    # (internal docker network address in prod, localhost in local dev).
    # minio_public_endpoint is what browsers use for presigned uploads and
    # for the object URLs stored in the DB — must be a publicly reachable
    # host, since SigV4 signs the Host header (see blob_storage.py).
    minio_endpoint: str = "http://localhost:9000"
    minio_public_endpoint: str = "http://localhost:9000"
    minio_access_key: str = "dev-only-minio-access-key"
    minio_secret_key: str = "dev-only-minio-secret-key"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
