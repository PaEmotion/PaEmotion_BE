
from services.report.data import type_data_read
from ai.typeClassification import classification_type
from sqlalchemy.orm import Session

def classify_type (db: Session, userId: int, year: int, month: int):
    # 데이터 조회하기
    df = type_data_read(db, userId)
    if df.empty:
        print("조회된 데이터가 없습니다.")
        return []
    
    pred_labels = classification_type(df, year, month)

    return pred_labels