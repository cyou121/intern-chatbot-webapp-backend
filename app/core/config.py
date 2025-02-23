from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ACCESS_SECRET_KEY: str = "access_secret_key"
    REFRESH_SECRET_KEY: str = "refresh_secret_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    database_url: str
    openai_api_key: str
    openai_model: str
    gemini_api_key_path: str
    GEMINI_MODEL: str
    PROJECT_ID: str
    LOCATION : str
    YOUR_ACCESS_KEY : str
    YOUR_SECRET_KEY : str
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
