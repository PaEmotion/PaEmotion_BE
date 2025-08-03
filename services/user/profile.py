from schemas.user import NicknameUpdate
from models.user import User
from sqlalchemy.orm import Session

class ProfileService:

    @staticmethod
    def update_nickname(userId: int, request: NicknameUpdate, db:Session):
        user = db.query(User).filter(User.userId == userId).first()
        if not user:
            raise Exception("User not found")
        
        user.nickname = request.new_nickname
        db.commit()
        db.refresh(user)
        return {"message" : "닉네임이 변경되었습니다."}