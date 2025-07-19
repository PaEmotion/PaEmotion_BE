# ai/model_training.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
from utils import make_sliding_window_multi
from services.report.data import data_read

def budgetTraining():
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

'''
 # 실제 데이터로 학습하는 법, 서비스 사용시 학습시키지 않음
def budgetTraining():
    # 1. 데이터 로드 (DB로부터)
    df = data_read()  # <- csv에서 DB로 변경됨

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
    print("모델 저장 완료: rf_model.pkl")
'''