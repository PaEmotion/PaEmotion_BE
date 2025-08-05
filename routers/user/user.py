from fastapi import APIRouter, HTTPException, status, Depends, Body
from sqlalchemy.orm import Session
from schemas.user import UserSignup, UserLogin, PasswordUpdate, PasswordReset, NicknameUpdate
from services.user.user import UserService
from services.user.password import PasswordService
from services.user.profile import ProfileService
from db.session import get_db
from models import User
from auth.email_token import verify_email_token, delete_token
from auth.jwt_token import get_current_user, create_access_token
from auth.dependencies import redis_client, SECRET_KEY, ALGORITHM
from utils.response import response_success, response_error

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup, db: Session = Depends(get_db)):
    try:
        created_user = await UserService.signup(user, db)
        return response_success(data=created_user, message="회원가입 성공", status_code=201)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login")
async def login(user: UserLogin, db:Session=Depends(get_db)):
    try:
        result = await UserService.login(user, db)
        return response_success(result, message="로그인 성공")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me") # 정보를 db에서 받아오는 것이므로 User 순서 반대
def myinfo(current_user : User = Depends(get_current_user)):
    result = {
        "email" : current_user.email,
        "name" : current_user.name,
        "nickname" : current_user.nickname
    }
    return response_success(data=result, message="마이페이지 출력 성공")

@router.put("/password")
def update_password(
    request: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = PasswordService.update_password(current_user.userId, request, db)
    return response_success(data=result, message="비밀번호 변경 성공")

@router.post("/token/refresh")
def refresh_access_token(refresh_token:str = Body(..., embed=True)):
    result = UserService.refresh_access_token(
        refresh_token= refresh_token,
        redis_client=redis_client,
        secret_key=SECRET_KEY,
        algorithm=ALGORITHM,
        create_access_token=create_access_token
    )
    return response_success(data=result, message="리프레쉬 토큰 발급 성공", status_code=201)

@router.post("/reset-password")
def reset_password(data: PasswordReset, db: Session = Depends(get_db)):
    
    email = verify_email_token(data.token)
    if email is None:
        raise HTTPException(status_code=400, detail="유효하지 않은 토큰입니다.")
    
    PasswordService.reset_password(email=email, new_password=data.new_password, db=db)
    delete_token(data.token)

    return response_success(message="비밀번호 초기화 성공")

@router.put("/nickname")
def update_nickname(
    request: NicknameUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        result = ProfileService.update_nickname(current_user.userId, request, db)
        return response_success(data=result, message="닉네임이 변경되었습니다.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))