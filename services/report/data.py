from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional

from models.record import Record
import pandas as pd

# ML 모델 학습용 / 예측용 데이터 로드 함수, DataFrame 형태로 반환
def data_read(db: Session, user_id: int, spend_date: Optional[str] = None) -> pd.DataFrame:
   
    query = db.query(Record).filter(Record.userId == user_id)
    if spend_date:
        query = query.filter(func.date(Record.spendDate) == spend_date)

    records = query.all()

    if not records:
        return pd.DataFrame()

    data = [{
        'userId': r.userId,
        'spendCost': r.spendCost,
        'spendDate': r.spendDate,
        'spendCategoryId' : r.spendCategoryId,
        'spendId':r.spendId
    } for r in records]

    df = pd.DataFrame(data)
    return df