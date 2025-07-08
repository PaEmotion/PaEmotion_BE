from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
import os

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
EMAIL_TOKEN_EXPIRE_MINUTES = int(os.environ.get("EMAIL_TOKEN_EXPIRE_MINUTES"))

def create_email_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

