import numpy as np
import pandas as pd
import ast
from scipy.stats import entropy

# 컬럼에 들어있는 데이터가 문자열 형태여야함 -> 아닐 경우의 예외 처리
def safe_literal_eval(x):
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except Exception:
            return []  
    else:
        return x
    
def type_process(df):
    # 로그 변환
    df['log_spendCost'] = np.log1p(df['spendCost'])

    # budgets, actuals 문자열 → 리스트
    df['budgets'] = df['budgets'].apply(safe_literal_eval)
    df['actuals'] = df['actuals'].apply(safe_literal_eval)

    # budgets이 리스트인지 확인 + 인덱스 범위 오류 예외 처리
    def safe_get_budget(row):
        budgets = row['budgets']
        idx = row['spendCategoryId'] - 1
        if isinstance(budgets, list) and 0 <= idx < len(budgets):
            return budgets[idx]
        else:
            return 0

    # actuals가 리스트인지 확인 + 인덱스 범위 오류 예외 처리
    def safe_get_actual(row):
        actuals = row['actuals']
        idx = row['spendCategoryId'] - 1
        if isinstance(actuals, list) and 0 <= idx < len(actuals):
            return actuals[idx]
        else:
            return 0

    df['budget_for_category'] = df.apply(safe_get_budget, axis=1)
    df['actual_for_category'] = df.apply(safe_get_actual, axis=1)

    # 예산 대비 소비 비율
    df['over_budget_ratio'] = df['spendCost'] / df['budget_for_category']
    
    # 1) 감정 소비 비중 (max)
    emotion_counts = df.groupby(['userId', 'emotionCategoryId']).size().unstack(fill_value=0)
    emotion_ratios = emotion_counts.div(emotion_counts.sum(axis=1), axis=0)
    df = df.merge(
        emotion_ratios.max(axis=1).rename('max_emotion_ratio').reset_index(),
        on='userId', how='left'
    )

    # 2) 감정 엔트로피
    def calc_entropy(row):
        probs = row / row.sum()
        return entropy(probs, base=2)
    emotion_entropy = emotion_counts.apply(calc_entropy, axis=1).rename('emotion_entropy').reset_index()
    df = df.merge(emotion_entropy, on='userId', how='left')

    # 3) 모임/선물 소비 비중
    category_counts = df.groupby(['userId', 'spendCategoryId']).size().unstack(fill_value=0)
    category_ratios = category_counts.div(category_counts.sum(axis=1), axis=0)
    category_ratios['meeting_gift_ratio'] = category_ratios.get(9, 0) + category_ratios.get(11, 0)
    df = df.merge(category_ratios['meeting_gift_ratio'].reset_index(), on='userId', how='left')

    # 4) 소비 표준편차 / 평균 비율
    user_stats = df.groupby('userId')['spendCost'].agg(['mean', 'std']).reset_index()
    user_stats['std_over_mean'] = user_stats['std'] / user_stats['mean']
    df = df.merge(user_stats[['userId', 'std_over_mean']], on='userId', how='left')

    # 5) 가장 많이 소비한 카테고리 비중
    cat_counts = df.groupby(['userId', 'spendCategoryId']).size().unstack(fill_value=0)
    cat_ratios = cat_counts.div(cat_counts.sum(axis=1), axis=0)
    df = df.merge(
        cat_ratios.max(axis=1).rename('max_category_ratio').reset_index(),
        on='userId', how='left'
    )

    return df