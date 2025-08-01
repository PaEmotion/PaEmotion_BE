from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    EMAIL_TOKEN_EXPIRE_MINUTES : int
    SMTP_USER :str
    SMTP_PASSWORD : str
    OPENAI_API_KEY : str
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES : int

    class Config:
        env_file = ".env"

settings = Settings()
