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
    FCM_JSON_PATH : str

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.OPENAI_API_KEY = self.OPENAI_API_KEY.strip()

settings = Settings()
