from redis import Redis
from auth.settings import settings
import redis
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User

redis_client = redis.Redis(host='localhost', port=6379, db=0)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
DATABASE_URL = settings.DATABASE_URL
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
EMAIL_TOKEN_EXPIRE_MINUTES = settings.EMAIL_TOKEN_EXPIRE_MINUTES
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
OPENAI_API_KEY = settings.OPENAI_API_KEY
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES= settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES

def get_all_user_ids() -> list[int]:
    db: Session = next(get_db())
    user_ids = db.query(User.userId).all()
    return [uid[0] for uid in user_ids]