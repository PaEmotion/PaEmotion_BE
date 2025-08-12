from services.ml.data import read_prediction_data
from ai.budget.prediction import budget_predict
from sqlalchemy.orm import Session
import numpy as np
import logging
logger = logging.getLogger(__name__)

def training_and_prediction (db: Session, userId: int):
    df = read_prediction_data(db, userId)
    if df.empty:
        logger.warning("⚠️ 조회된 데이터가 없습니다.")
        return []
    
    preds = budget_predict(df, model_path='ai/budget/predict.pkl')
    if isinstance(preds, tuple) and len(preds) == 2:
        preds_list, mae = preds
        first_pred = preds_list[0] if len(preds_list) > 0 else None
        return first_pred, mae
    else:
        first_pred = preds[0] if isinstance(preds, (list, np.ndarray)) and len(preds) > 0 else preds
        return first_pred