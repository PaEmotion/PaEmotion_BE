# ai/model_predict.py
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error
from utils import make_sliding_window_multi

def budgetPrediction(model_path='rf_model.pkl', test_csv_path='../data/test.csv'):
    # 1. 테스트 데이터 로드
    df = pd.read_csv(test_csv_path)
    df['spendDate'] = pd.to_datetime(df['spendDate'])
    df['week'] = df['spendDate'].dt.isocalendar().week
    df['avg_spend'] = df.groupby('userId')['spendCost'].transform('mean')

    # 2. 주별 집계
    weekly = df.groupby(['userId', 'week']).agg({
        'spendCost': 'sum',
        'avg_spend': 'mean'
    }).reset_index()

    # 3. 슬라이딩 윈도우 함수 적용
    X_test, y_test = make_sliding_window_multi(weekly, window=8)

    # 4. 모델 불러오기 & 예측
    model = joblib.load(model_path)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    print(f"✅ 테스트 MAE: {mae:,.0f}원")

    return preds, y_test, mae

''' # 실제 배포용 
def predict_spending(test_df: pd.DataFrame, model_path='rf_model.pkl') -> np.ndarray:
    test_df['spendDate'] = pd.to_datetime(test_df['spendDate'])
    test_df['week'] = test_df['spendDate'].dt.isocalendar().week
    test_df['avg_spend'] = test_df.groupby('userId')['spendCost'].transform('mean')

    weekly = test_df.groupby(['userId', 'week']).agg({
        'spendCost': 'sum',
        'avg_spend': 'mean'
    }).reset_index()

    X_test, _ = make_sliding_window_multi(weekly, window=8)

    model = joblib.load(model_path)
    preds = model.predict(X_test)
    return preds

'''