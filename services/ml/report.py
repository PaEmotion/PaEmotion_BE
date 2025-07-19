from ai.utils import make_sliding_window_multi
from services.report.data import data_read
from ai import budgetTraining, budgetPrediction
import joblib

def training_and_prediction (userId:int):
    # 1. 데이터 조회하기
    df = data_read(userId)

    # 2. 데이터 전처리하기
    X, _ = make_sliding_window_multi(df)

    # 3. 예측하기
    model = joblib.load("ai/rf_model.pkl")
    y_pred = budgetPrediction(model, X[-1])
    return y_pred