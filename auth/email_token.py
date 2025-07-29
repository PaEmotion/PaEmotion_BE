from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from auth.dependencies import SECRET_KEY, ALGORITHM, EMAIL_TOKEN_EXPIRE_MINUTES

def create_email_token(email: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=EMAIL_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

