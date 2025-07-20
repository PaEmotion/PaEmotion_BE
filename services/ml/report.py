
from services.report.data import data_read
from ai.budgetPrediction import budget_predict
import joblib
from sqlalchemy.orm import Session
from typing import Optional



def training_and_prediction (db: Session, userId: int, spend_date: Optional[str] = None):
    # 1. 데이터 조회하기
    df = data_read(db, userId, spend_date)
    if df.empty:
        print("⚠️ 조회된 데이터가 없습니다.")
        return []
    
    preds = budget_predict(df, model_path='ai/rf_model.pkl')
    return preds.tolist() if hasattr(preds, 'tolist') else preds
