from services.ml.data import read_prediction_data
from ai.budget.prediction import budget_predict, budget_predict_test
from sqlalchemy.orm import Session
import numpy as np

def training_and_prediction (db: Session, userId: int):
    df = read_prediction_data(db, userId)
    if df.empty:
        print("⚠️ 조회된 데이터가 없습니다.")
        return []
    
    preds = budget_predict(df, model_path='ai/budget/predict.pkl')
    if isinstance(preds, tuple) and len(preds) == 2:
        preds_list, mae = preds
        first_pred = preds_list[0] if len(preds_list) > 0 else None
        return first_pred, mae
    else:
        first_pred = preds[0] if isinstance(preds, (list, np.ndarray)) and len(preds) > 0 else preds
        return first_pred

def training_and_prediction_test (db:Session, userId: int) :
    df = read_prediction_data(db, userId)
    if df.empty:
        print("⚠️ 조회된 데이터가 없습니다.")
        return []
    
    preds = budget_predict_test(df, model_path='ai/budget/predict.pkl')
    if isinstance(preds, tuple) and len(preds) == 2:
        preds_list, mae = preds
        first_pred = preds_list[0] if len(preds_list) > 0 else None
        return first_pred, mae
    else:
        first_pred = preds[0] if isinstance(preds, (list, np.ndarray)) and len(preds) > 0 else preds
        return first_pred, None
