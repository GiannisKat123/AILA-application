from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OLLAMA_SERVER_URL: str
    FRONTEND_URL: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_DATABASE_NAME: str
    DB_DRIVER_NAME: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    API_KEY: str
    SECRET_KEY:str
    ALGORITHM:str
    VITE_API_URL: str 
    APP_PASSWORD: str
    SENDER_EMAIL: str
    class Config:
        env_file = ".env"

settings = Settings()
