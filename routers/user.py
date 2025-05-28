from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schemas.user import UserCreate
from services.userService import UserService
from db.session import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    try:
        created_user = await UserService.create_user(user, db)
        return {
            "msg": "회원가입 성공",
            "user": created_user
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
