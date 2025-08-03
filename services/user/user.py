from schemas.user import UserSignup, UserLogin
from models.user import User
from sqlalchemy.orm import Session
from auth.jwt_token import create_access_token, create_refresh_token
import hashlib
from fastapi import HTTPException
from jose import jwt, JWTError
from fastapi import HTTPException, status
from auth.dependencies import REFRESH_TOKEN_EXPIRE_DAYS, redis_client

class UserService:
    @staticmethod
    async def signup(user: UserSignup, db: Session) -> dict:

        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("이미 존재하는 이메일입니다.")
        
        is_verified = redis_client.get(f"verified:{user.email}")
        if not is_verified:
            raise ValueError("이메일 인증을 먼저 완료해 주세요.")

        # 비밀번호 해싱
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

        # 새로운 유저 객체 생성
        new_user = User(
            email=user.email,
            name=user.name,
            nickname=user.nickname,
            password=hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "email": new_user.email,
            "name": new_user.name,
            "nickname": new_user.nickname
        }
    
    @staticmethod
    async def login(user: UserLogin, db:Session) -> dict:

        existing_user = db.query(User).filter(User.email == user.email).first()
        if not existing_user:
            raise ValueError("존재하지 않는 회원입니다.")
        
        # 받은 비밀번호 해싱
        hashed_input_pw = hashlib.sha256(user.password.encode()).hexdigest()

        # 원래의 비밀번호와 일치하는지 검증
        if existing_user.password != hashed_input_pw:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        
        access_token = create_access_token(data={"sub": str(existing_user.userId)})
        refresh_token = create_refresh_token(data={"sub":str(existing_user.userId)})

        redis_client.set(f"refresh_token:{existing_user.userId}", refresh_token, ex= REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60)

        return {
            "userId": existing_user.userId,
            "email": existing_user.email,
            "name" : existing_user.name,
            "nickname" : existing_user.nickname,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str, redis_client, secret_key, algorithm, create_access_token):
        try:
            payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
            userId = int(payload.get("sub"))
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 리프레쉬 토큰입니다.")
        
        stored_token = redis_client.get(f"refresh_token:{userId}")
        if stored_token is None or stored_token.decode() != refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")
        
        new_access_token = create_access_token(data={"sub":str(userId)})
        return {"access_token":new_access_token, "token_type":"bearer"}