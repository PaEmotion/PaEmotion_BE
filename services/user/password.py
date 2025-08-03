from schemas.user import PasswordUpdate, NicknameUpdate
from models.user import User
from sqlalchemy.orm import Session
import hashlib
from fastapi import HTTPException
from fastapi import HTTPException

class PasswordService:
    
    @staticmethod
    def update_password(userId: int, request: PasswordUpdate, db:Session):
        user = db.query(User).filter(User.userId == userId).first()

        if not user:
            raise HTTPException(status_code = 404, detail="유저를 찾을 수 없습니다.")

        hashed_current_password = hashlib.sha256(request.current_password.encode()).hexdigest()

        if user.password != hashed_current_password:
            raise HTTPException(status_code = 400, detail = "현재 비밀번호가 일치하지 않습니다.")

        hashed_new_password = hashlib.sha256(request.new_password.encode()).hexdigest()
        user.password = hashed_new_password
        db.commit()
        
        return {"message" : "성공적으로 비밀번호가 변경되었습니다."}
    
    @staticmethod
    def reset_password(email: str, new_password: str, db:Session):
        existing_user = db.query(User).filter(User.email == email).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        existing_user.password = hashed_password
        db.commit()

        return {"message" : "성공적으로 비밀번호가 재설정 되었습니다."}
    