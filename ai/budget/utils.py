import numpy as np
import pandas as pd

## ===== 날짜 처리 ===== 
def preprocess_weekly_spending(df):
    df['spendDate'] = pd.to_datetime(df['spendDate'])
    df['week'] = df['spendDate'].dt.isocalendar().week

    ## ===== 주별 소비 집계 =====
    weekly_spending = df.groupby(['userId', 'week'])['spendCost'].sum().reset_index()
    weekly_spending['avg_spend'] = weekly_spending.groupby('userId')['spendCost'].transform('mean')

    return weekly_spending

## ===== 반복 소비 카테고리 =====
def add_category_repeat_features(df, window=3):
    df = df.sort_values(['userId', 'spendDate'])
    df['week'] = df['spendDate'].dt.isocalendar().week

    # 빈도 / 금액 / 병합
    weekly_freq = df.groupby(['userId', 'week', 'spendCategoryId'])['spendId'].count().reset_index(name='count')
    weekly_amt = df.groupby(['userId', 'week', 'spendCategoryId'])['spendCost'].sum().reset_index(name='amount')
    weekly = pd.merge(weekly_freq, weekly_amt, on=['userId', 'week', 'spendCategoryId'])
    
    feature_rows = []

    for user in df['userId'].unique():
        user_weeks = weekly[weekly['userId'] == user]['week'].unique()
        for w in user_weeks:
            recent_weeks = list(range(w - window, w))
            recent = weekly[(weekly['userId'] == user) & (weekly['week'].isin(recent_weeks))]
            
            row = {'userId': user, 'week': w}
            for cat_id in range(1, 11):
                cat_data = recent[recent['spendCategoryId'] == cat_id]
                row[f'cat{cat_id}_freq'] = cat_data['count'].sum()
                row[f'cat{cat_id}_amount'] = cat_data['amount'].sum()
            feature_rows.append(row)

    return pd.DataFrame(feature_rows)

## ===== 주력 루틴 소비 평균 금액 =====
def add_main_routine_avg(df):
    df['main_cat'] = df[[f'cat{i}_freq' for i in range(1, 11)]].idxmax(axis=1)
    df['main_cat_id'] = df['main_cat'].str.extract(r'cat(\d+)_freq').astype(int)
    df['main_cat_total'] = df.apply(
        lambda row: row.get(f"cat{int(row['main_cat_id'])}_amount", 0), axis=1)
    df['main_cat_freq'] = df.apply(
        lambda row: row.get(f"cat{int(row['main_cat_id'])}_freq", 0), axis=1)
    df['main_cat_avg_amount'] = df.apply(
        lambda row: row['main_cat_total'] / row['main_cat_freq'] if row['main_cat_freq'] > 0 else 0, axis=1)
    df['expected_routine_spend'] = (df['main_cat_freq'] / 3) * df['main_cat_avg_amount']
    return df

## ===== sliding window 방식으로 데이터셋 구성 =====
def make_features_with_info(df, window=8):
    X, info = [], []
    for user in df['userId'].unique():
        user_df = df[df['userId'] == user].sort_values('week')
        spend = user_df['spendCost'].values
        avg = user_df['avg_spend'].values
        cat_feats = user_df[[f'cat{i}_freq' for i in range(1, 11)]].values
        routine_avg = user_df['main_cat_avg_amount'].values
        routine_spend = user_df['expected_routine_spend'].values

        if len(spend) < window + 1:
            continue

        for i in range(len(spend) - window) :
            spend_slice = spend[i:i+window]
            avg_slice = avg[i:i+window]
            cat_slice = cat_feats[i:i+window]
            routine_avg_slice = routine_avg[i:i+window]
            routine_spend_slice = routine_spend[i:i+window]

            features = np.concatenate([
                spend_slice, 
                avg_slice, 
                cat_slice.flatten(),
                routine_avg_slice,
                routine_spend_slice
                
            ])
        
            X.append(features)
            info.append((user, user_df['week'].iloc[i+window]))

    return np.array(X), info

def full_preprocess(df, window=8, cat_window=3):
    weekly_spending = preprocess_weekly_spending(df)
    cat_feat = add_category_repeat_features(df, window=cat_window)
    weekly = pd.merge(weekly_spending, cat_feat, on=['userId', 'week'], how='left').fillna(0)
    weekly = add_main_routine_avg(weekly)
    X, info = make_features_with_info(weekly, window=window)
    return X, info