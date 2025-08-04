from fastapi import APIRouter, Depends, HTTPException, Query
from services.ml.type import classify_type
from sqlalchemy.orm import Session
from db.session import get_db
from utils.response import response_success
from models.user import User
from auth.jwt_token import get_current_user

router = APIRouter(prefix="/ml")

# 테스트용 라우터

@router.get("/classify")
def typeClassification(
    current_user: User = Depends(get_current_user),
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    pred_labels = classify_type(db, current_user.userId, year, month)
    if not pred_labels:
        return response_success(
            data=[],
            message="조회된 데이터가 없습니다."
        )
    
    return response_success(
        data=pred_labels,
        message="소비 성향 분류 결과 조회 완료"
    )