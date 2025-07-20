# ai/model_predict.py
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error
from ai.utils import full_preprocess

def budget_predict(test_df=None, model_path='ai/rf_model.pkl', window=8, cat_window=3):

    if test_df is None:
        print("⚠️ 예측할 충분한 데이터가 없습니다. 빈 리스트 반환합니다.")
        return []

    X_test, y_test = full_preprocess(test_df, window=window, cat_window=cat_window)

    print(f"DEBUG: X_test 길이 = {len(X_test)}, y_test 길이 = {len(y_test)}")

    if len(X_test) == 0:
        print("⚠️ 예측할 충분한 데이터가 없습니다. 조금 더 나중에 시도하십시오.")
        return []
    
    model = joblib.load(model_path)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    print(f"✅ 테스트 MAE: {mae:,.0f}원")

    return preds


''' # 실제 배포용 
def budget_predict(test_df: pd.DataFrame, model_path='ai/rf_model.pkl') -> np.ndarray:
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