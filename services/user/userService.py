from schemas.user import UserCreate, UserLogin
from models.user import User
from db.session import get_db
from sqlalchemy.orm import Session
import hashlib, redis
from auth.jwt_token import create_access_token

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class UserService:
    @staticmethod
    async def create_user(user: UserCreate, db: Session) -> dict:
        # 이미 존재하는 이메일 확인
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

        # DB에 저장
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
        # 존재하는 이메일인지 확인
        existing_user = db.query(User).filter(User.email == user.email).first()
        if not existing_user:
            raise ValueError("존재하지 않는 회원입니다.")
        
        # 받은 비밀번호 해싱
        hashed_input_pw = hashlib.sha256(user.password.encode()).hexdigest()

        # 원래의 비밀번호와 일치하는지 검증
        if existing_user.password != hashed_input_pw:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        
        access_token = create_access_token(data={"sub": str(existing_user.userId)})
        
        return {
            "email": existing_user.email,
            "name" : existing_user.name,
            "nickname" : existing_user.nickname,
            "access_token": access_token,
            "token_type": "bearer"
        }
