from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    WEATHER_API_KEY: str

    class Config:
        env_file = ".env"
        cache_intensive = True


settings = Settings()
