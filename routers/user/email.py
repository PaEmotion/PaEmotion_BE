from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from schemas.emailRequestSchema import EmailRequestSchema
from services.user.emailService import EmailService
from db.session import get_db
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os, redis

templates = Jinja2Templates(directory="templates")

router = APIRouter()

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
EMAIL_TOKEN_EXPIRE_MINUTES = int(os.environ.get("EMAIL_TOKEN_EXPIRE_MINUTES"))

def save_email_verification_token(email: str, token: str, expire_seconds: int = 3600):
    redis_client.set(token, email, ex=expire_seconds)

def verify_email_token(token: str) -> str | None:
    return redis_client.get(token)

def delete_token(token: str):
    redis_client.delete(token)

# 1번 - 사용자가 이메일 인증을 요청할 때 호출
@router.post("/request-email-verification")
async def request_email_verification(data: EmailRequestSchema, db: Session = Depends(get_db)):
    try:
        token = await EmailService.send_verification_email(data.email, db) # 이메일 서비스를 불러옴
        return {"message": "인증 이메일이 전송되었습니다."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="이메일 인증 요청 중 오류가 발생했습니다.")

# 4번 - 이메일 인증 링크에서 호출되는 엔드포인트 -> 토큰 검증을 통해 성공/실패에 따른 화면을 출력하게 함
@router.get("/verify-email", response_class=HTMLResponse)
def verify_email(token:str, request :Request, db:Session = Depends(get_db)):
    email = verify_email_token(token)

    if email is None:
        return templates.TemplateResponse("verify_fail.html", {"request": request})
    
    redis_client.set(f"verified:{email}", "true", ex=3600)  
    delete_token(token)

    return templates.TemplateResponse("verify_success.html", {"request": request})