from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    VERIFICATION_TOKEN_EXPIRE_MINUTES: str
    SECRET_KEY: str
    ALGORITHM: str 
    APP_PASSWORD: str
    SENDER_EMAIL: str
    OPENAI_API_KEY:str
    HF_TOKEN:str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_DATABASE_NAME: str
    DB_DRIVER_NAME: str
    OPEN_AI_MODEL:str
    AWS_PROFILE:str
    AWS_ACCESS_KEY:str
    AWS_SECRET_KEY:str
    BUCKET_NAME:str
    REGION:str
    INIT_MODE:str
    FRONTEND_URL:str

    class Config:
        env_file = ".env"

settings = Settings()
