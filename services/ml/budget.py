from services.ml.data import read_budget_data
from ai.budget.prediction import budget_predict
from sqlalchemy.orm import Session

def training_and_prediction (db: Session, userId: int):
    df = read_budget_data(db, userId)
    if df.empty:
        print("⚠️ 조회된 데이터가 없습니다.")
        return []
    
    preds = budget_predict(df, model_path='ai/rf_model.pkl')
    return preds.tolist() if hasattr(preds, 'tolist') else preds
