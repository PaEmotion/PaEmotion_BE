# ai/model_predict.py
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import mean_absolute_error
from utils import make_sliding_window_multi

# 1. 테스트 데이터 로드
df = pd.read_csv('../data/test.csv')
df['spendDate'] = pd.to_datetime(df['spendDate'])
df['week'] = df['spendDate'].dt.isocalendar().week
df['avg_spend'] = df.groupby('userId')['spendCost'].transform('mean')

# 2. 주별 집계
weekly = df.groupby(['userId', 'week']).agg({
    'spendCost': 'sum',
    'avg_spend': 'mean'
}).reset_index()

# 3. 슬라이딩 윈도우
X_test, y_test = make_sliding_window_multi(weekly, window=8)

# 4. 모델 불러오기 & 예측
model = joblib.load('rf_model.pkl')
preds = model.predict(X_test)

# 5. 평가
mae = mean_absolute_error(y_test, preds)
print(f"✅ 테스트 MAE: {mae:,.0f}원")
