from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""
    app_title: str = 'MenuAPI'
    description: str = 'API сервис для меню'
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cache_lifetime: int = 60
    google_sheet_id: str
    use_google_sheets: bool = False
    type: str | None = None
    project_id: str | None = None
    private_key_id: str | None = None
    private_key: str | None = None
    client_email: str | None = None
    client_id: str | None = None
    auth_uri: str | None = None
    token_uri: str | None = None
    auth_provider_x509_cert_url: str | None = None
    client_x509_cert_url: str | None = None
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()

db_url = (
    f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}'
    f'@{settings.db_host}:{settings.db_port}/{settings.db_name}'
)
