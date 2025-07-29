from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserLogin, PasswordUpdate
from services.user.userService import UserService
from db.session import get_db
from models import User
from auth.jwt_token import get_current_user, create_access_token
from auth.dependencies import redis_client, SECRET_KEY, ALGORITHM

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

@router.put("/password")
def update_password(
    request: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return UserService.update_password(current_user.userId, request, db)

@router.post("/token/refresh")
def refresh_access_token(refresh_token:str = Body(..., embed=True)):
    return UserService.refresh_access_token(
        refresh_token= refresh_token,
        redis_client=redis_client,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        create_access_token=create_access_token
    )