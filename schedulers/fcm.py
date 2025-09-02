from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db.session import get_db
from auth.dependencies import redis_client
from utils.response import response_success

router = APIRouter(prefix="/users", tags=["users"])

# 요청 바디 스키마
class FCMTokenRequest(BaseModel):
    userId: int
    fcmToken: str

@router.post("/fcm-token")
def save_fcm_token(request: FCMTokenRequest):
    redis_client.set(f"user:{request.userId}:fcm", request.fcmToken, ex=14*24*3600)
    return response_success(message= "토큰이 redis에 저장됨")
