from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg://twistfit:twistfit@localhost:5432/twistfit_dev"
    jwt_secret: str = "dev-only-insecure-jwt-secret"
    cors_origins: str = "http://localhost:3000"
    cookie_domain: str | None = None
    cookie_secure: bool = False
    gemini_api_key: str = "dev-only-placeholder-gemini-key"
    catvton_service_url: str = "http://localhost:8001"
    catvton_api_key: str = "dev-only-placeholder-catvton-key"
    flux_api_base_url: str = "https://api.bfl.ai"
    flux_api_key: str = "dev-only-placeholder-flux-api-key"
    frontend_base_url: str = "http://localhost:3000"
    azure_storage_connection_string: str = (
        "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;"
        "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
        "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
