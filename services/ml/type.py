from services.ml.data import read_type_data
from ai.type.classification import classification_type
from sqlalchemy.orm import Session

def classify_type (db: Session, userId: int, year: int, month: int):
    df = read_type_data(db, userId)
    if df.empty:
        print("조회된 데이터가 없습니다.")
        return []
    
    pred_labels = classification_type(df, year, month)

    return pred_labels