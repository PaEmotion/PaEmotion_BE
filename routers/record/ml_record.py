from typing import Optional, List
from fastapi import APIRouter, Path, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from db.session import get_db
from services.record.ml_record import records_readbylist as ml_records_readbylist
from schemas.record import RecordsRead

router = APIRouter(prefix="/ml/records", tags=["ml_records"])

"""
모델 학습용 유저별/날짜별 소비내역 조회 API
유저아이디만 URL로 받음 -> 유저별 소비내역 조회
유저아이디 URL로 받고 쿼리파라미터로 날짜 받음 -> 유저별로 날짜별 소비내역 조회
"""
@router.get("/readbylist/{userId}", response_model=List[RecordsRead])
def readbylist(
    userId: int = Path(...),
    spendDate: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    result = ml_records_readbylist(db=db, user_id=userId, spend_date=spendDate)
    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result
