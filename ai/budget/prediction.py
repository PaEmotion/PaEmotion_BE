# ai/model_predict.py
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error
from ai.budget.utils import full_preprocess, full_preprocess_test

def budget_predict(test_df=None, model_path='ai/budget/predict.pkl', window=8, cat_window=3):

    if test_df is None:
        print("⚠️ 예측할 충분한 데이터가 없습니다. 빈 리스트 반환합니다.")
        return []

    X_test, info = full_preprocess(test_df, window=window, cat_window=cat_window)

    if len(X_test) <3 :
        print("⚠️ 예측할 충분한 데이터가 없습니다. 조금 더 나중에 시도하십시오.")
        return []
    
    model = joblib.load(model_path)
    preds = model.predict(X_test)

    return preds


## 테스트용
def budget_predict_test(test_df=None, model_path='ai/budget/predict.pkl', window=8, cat_window=3):

    if test_df is None:
        print("⚠️ 예측할 충분한 데이터가 없습니다. 빈 리스트 반환합니다.")
        return []

    X_test, y_test, info = full_preprocess_test(test_df, window=window, cat_window=cat_window)

    print(f"DEBUG: X_test 길이 = {len(X_test)}, y_test 길이 = {len(y_test)}")

    if len(X_test) < 3 :
        print(f"⚠️ {window} 주 이상 필요, 현재 {len(X_test)} 세트.")
        return []
    
    model = joblib.load(model_path)
    preds = model.predict(X_test)

    mae = mean_absolute_error(y_test, preds)
    print(f"✅ 테스트 MAE: {mae:,.0f}원")

    return preds, mae