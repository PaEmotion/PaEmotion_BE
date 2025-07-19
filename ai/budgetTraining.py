# ai/model_training.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from utils import make_sliding_window_multi

# 1. 데이터 로드
df = pd.read_csv('../data/train.csv')
df['spendDate'] = pd.to_datetime(df['spendDate'])
df['week'] = df['spendDate'].dt.isocalendar().week

# 2. 유저 평균 소비액 추가
avg = df.groupby('userId')['spendCost'].transform('mean')
df['avg_spend'] = avg

# 3. 주별 소비 총합
weekly = df.groupby(['userId', 'week']).agg({
    'spendCost': 'sum',
    'avg_spend': 'mean'
}).reset_index()

# 4. 피처 생성
X, y = make_sliding_window_multi(weekly, window=8)

# 5. 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 6. 저장
joblib.dump(model, 'rf_model.pkl')
print("🎉 모델 저장 완료: rf_model.pkl")
