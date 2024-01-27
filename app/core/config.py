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
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()

db_url = (
    f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}'
    f'@{settings.db_host}:{settings.db_port}/{settings.db_name}'
)
