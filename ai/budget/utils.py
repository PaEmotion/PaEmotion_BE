import numpy as np
import pandas as pd

# 주별 소비 총액 + 유저별 평균 소비액 계산 -> 병합
def preprocess_weekly_spending(df):
    df['spendDate'] = pd.to_datetime(df['spendDate'])
    df['week'] = df['spendDate'].dt.isocalendar().week

    weekly_spending = df.groupby(['userId', 'week'])['spendCost'].sum().reset_index()
    avg_spending = df.groupby('userId')['spendCost'].mean().reset_index(name='avg_spend')

    weekly_spending = pd.merge(weekly_spending, avg_spending, on='userId', how='left')
    return weekly_spending

# 최근 window주 동안 카테고리별 소비 빈도 계산
def add_category_repeat_features(df, window=3):
    df = df.sort_values(['userId', 'spendDate'])
    df['week'] = df['spendDate'].dt.isocalendar().week

    weekly = df.groupby(['userId', 'week', 'spendCategoryId'])['spendId'].count().reset_index(name='count')
    feature_rows = []

    for user in df['userId'].unique():
        user_weeks = weekly[weekly['userId'] == user]['week'].unique()
        for w in user_weeks:
            recent_weeks = list(range(w - window, w))
            recent = weekly[(weekly['userId'] == user) & (weekly['week'].isin(recent_weeks))]

            cat_counts = recent.groupby('spendCategoryId').size().to_dict()
            row = {'userId': user, 'week': w}
            for cat_id in range(1, 11):  # 카테고리 개수에 맞게 조정 가능
                row[f'cat{cat_id}_freq'] = cat_counts.get(cat_id, 0)
            feature_rows.append(row)

    return pd.DataFrame(feature_rows)

# sliding window 방식
def make_features(df, window=8):
    X, y = [], []
    for user in df['userId'].unique():
        user_df = df[df['userId'] == user].sort_values('week')
        spend = user_df['spendCost'].values
        avg = user_df['avg_spend'].values
        cat_feats = user_df[[f'cat{i}_freq' for i in range(1, 11)]].values

        if len(spend) < window + 1:
            continue

        # 가장 최신 window만
        spend_slice = spend[-window:]
        avg_slice = avg[-window:]
        cat_slice = cat_feats[-window:]

        features = np.concatenate([spend_slice, avg_slice, cat_slice.flatten()])
        X.append(features)
        y.append(spend[-1])

    return np.array(X), np.array(y)

def full_preprocess(df, window=8, cat_window=3):
    weekly_spending = preprocess_weekly_spending(df)
    cat_freq = add_category_repeat_features(df, window=cat_window)
    weekly = pd.merge(weekly_spending, cat_freq, on=['userId', 'week'], how='left').fillna(0)

    X, y = make_features(weekly, window=window)
    return X, y