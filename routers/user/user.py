from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserLogin
from services.user.userService import UserService
from db.session import get_db
from models import User
from auth.jwt_token import get_current_user

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

@router.post("/login")
async def login(user: UserLogin, db:Session=Depends(get_db)):
    try:
        return await UserService.login(user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me") # 정보를 db에서 받아오는 것이므로 User 순서 반대
def myinfo(current_user : User = Depends(get_current_user)):
    return {
        "email" : current_user.email,
        "name" : current_user.name,
        "nickname" : current_user.nickname
    }