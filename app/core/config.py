from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_title: str = 'MenuAPI'
    description: str = 'API сервис для меню'
    database_url: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
