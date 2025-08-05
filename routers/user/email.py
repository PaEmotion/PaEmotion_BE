from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.email import Email
from services.user.email import EmailService
from db.session import get_db
from auth.email_token import verify_email_token, delete_token
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from auth.dependencies import redis_client
from utils.response import response_success

templates = Jinja2Templates(directory="templates")

router = APIRouter()

# 1번 - 사용자가 이메일 인증을 요청할 때 호출
@router.post("/request-email-verification")
async def request_email_verification(data: Email, db: Session = Depends(get_db)):
    try:
        token = await EmailService.send_verification_email(data.email, db) # 이메일 서비스를 불러옴
        return response_success(message="인증 이메일이 전송되었습니다.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="이메일 인증 요청 중 오류가 발생했습니다.")

# 4번 - 이메일 인증 링크에서 호출되는 엔드포인트 -> 토큰 검증을 통해 성공/실패에 따른 화면을 출력하게 함
@router.get("/verify-email", response_class=HTMLResponse)
def verify_email(token:str, request :Request, db:Session = Depends(get_db)):
    email = verify_email_token(token)

    if email is None:
        return templates.TemplateResponse("verify_signup_fail.html", {"request": request})
    
    redis_client.set(f"verified:{email}", "true", ex=3600)  
    delete_token(token)

    return templates.TemplateResponse("verify_signup_success.html", {"request": request})

@router.post("/request-password-reset")
async def request_password_reset(data: Email, db: Session = Depends(get_db)):
    try:
        token = await EmailService.send_password_reset_email(data.email, db) 
        return response_success(message="비밀번호 재설정 이메일이 전송되었습니다.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="비밀번호 재설정 이메일 전송중 오류가 발생했습니다.")

@router.get("/verify-password-reset-email")
def verify_password_reset_email(token:str, request: Request, db:Session=Depends(get_db)):
    email =  verify_email_token(token)

    if email is None:
        return templates.TemplateResponse("verify_reset_fail.html", {"request": request})
    
    redis_client.set(f"verified:{email}", "true", ex=3600)  
    
    return templates.TemplateResponse("verify_reset_success.html", {"request": request})