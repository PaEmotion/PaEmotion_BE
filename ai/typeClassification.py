import joblib
from sklearn.metrics import classification_report, accuracy_score
from ai.typeUtils import type_process

def classification_type(test_df, year, month, model_path='ai/type.pkl'):
    
    monthly_df = test_df[
        (test_df['spendDate'].dt.year == year) & (test_df['spendDate'].dt.month == month)
    ]
    
    if monthly_df.empty:
        return "데이터가 부족하여 소비 유형을 알 수 없습니다."

    processed_df = type_process(monthly_df)

    features = [
        'emotionCategoryId', 'spendCategoryId', 'log_spendCost', 'over_budget_ratio',
        'max_emotion_ratio', 'emotion_entropy', 'meeting_gift_ratio',
        'std_over_mean', 'max_category_ratio'
    ]

    # 모델 로드
    model = joblib.load(model_path)

    X_test = processed_df[features]

    # 예측
    y_pred = model.predict(X_test)

    pred_label = f"{y_pred[0]}형입니다"

    return pred_label
