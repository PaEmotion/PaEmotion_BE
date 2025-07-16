from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional

from models.record import Record

# 모델 학습용 유저별/날짜별 소비내역 조회 함수
def records_readbylist(db: Session, user_id: int, spend_date: Optional[date]):
    query = db.query(Record).filter(Record.userId == user_id)
    if spend_date is not None:
        query = query.filter(func.date(Record.spendDate) == spend_date)
    result = query.all()
    return result