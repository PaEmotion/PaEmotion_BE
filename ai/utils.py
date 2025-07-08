# ai/utils.py
import numpy as np

def make_sliding_window_multi(df, window=8):
    X, y = [], []
    for user in df['userId'].unique():
        user_df = df[df['userId'] == user].sort_values('week')
        spend = user_df['spendCost'].values
        avg_spend = user_df['avg_spend'].values
        if len(spend) < window + 1:
            continue
        for i in range(len(spend) - window):
            features = np.column_stack((spend[i:i+window], avg_spend[i:i+window]))
            X.append(features.flatten())
            y.append(spend[i+window])
    return X, y
