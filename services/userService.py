from schemas.user import UserCreate
from models.user import User
from db.session import get_db
from sqlalchemy.orm import Session
import hashlib

class UserService:
    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> dict:
        # 이미 존재하는 이메일 확인
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("이미 존재하는 이메일입니다.")
        
        # 비밀번호 해싱
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()

        # 새로운 유저 객체 생성
        new_user = User(
            email=user.email,
            name=user.name,
            nickname=user.nickname,
            password=hashed_password
        )

        # DB에 저장
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "email": new_user.email,
            "name": new_user.name,
            "nickname": new_user.nickname
        }
