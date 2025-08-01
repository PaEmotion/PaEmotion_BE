from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from auth.dependencies import SECRET_KEY, ALGORITHM, EMAIL_TOKEN_EXPIRE_MINUTES, PASSWORD_RESET_TOKEN_EXPIRE_MINUTES, redis_client

def create_email_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def create_password_reset_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub":email, "exp":expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def save_email_verification_token(email: str, token: str, expire_seconds: int = 3600):
    redis_client.set(token, email, ex=expire_seconds)

def verify_email_token(token: str) -> str | None:
    return redis_client.get(token)

def delete_token(token: str):
    redis_client.delete(token)
