import joblib
from ai.budget.utils import full_preprocess
import logging
logger = logging.getLogger(__name__)

def budget_predict(test_df=None, model_path='ai/budget/predict.pkl', window=8, cat_window=3):

    if test_df is None:
        logger.warning("⚠️ 예측할 충분한 데이터가 없습니다. 빈 리스트 반환합니다.")
        return []

    X_test, info = full_preprocess(test_df, window=window, cat_window=cat_window)

    if len(X_test) <3 :
        logger.warning("⚠️ 예측할 충분한 데이터가 없습니다. 조금 더 나중에 시도하십시오.")
        return []
    
    model = joblib.load(model_path)
    preds = model.predict(X_test)

    return preds