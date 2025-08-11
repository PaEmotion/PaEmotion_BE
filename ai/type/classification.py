import joblib
from sklearn.metrics import classification_report, accuracy_score
from ai.type.utils import type_process
import numpy as np

def classification_type(test_df, year, month, model_path='ai/type/classify.pkl'):
    
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

    X_test = X_test.replace([np.inf, -np.inf], np.nan)
    X_test = X_test.fillna(0) 

    # 예측
    y_pred = model.predict(X_test)

    # 출력을 위한 한글 이름 매핑
    label_map = {
        0: "감정소비형",
        1: "계획소비형",
        2: "충동소비형",
        3: "관계지향형",
        4: "무지출지향형",
        5: "소비성향편중형"
    }

    label_name = label_map.get(y_pred[0], f"{y_pred[0]}형")  # 예외처리
    pred_label = f"{label_name}입니다"

    return pred_label
