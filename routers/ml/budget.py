from fastapi import APIRouter, Depends
from services.ml.budget import training_and_prediction, training_and_prediction_test
from sqlalchemy.orm import Session
from db.session import get_db
from utils.response import response_success
from models.user import User
from auth.jwt_token import get_current_user
from numpy import expm1
router = APIRouter(prefix="/ml")

@router.get("/predict")
def budgetPrediction(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preds = training_and_prediction(db, current_user.userId)

    if preds is None:
        return response_success(data={}, message="예측할 데이터가 부족합니다.")

    real_pred = expm1(float(preds))
    formatted_pred = f"{round(real_pred):,}원"

    return response_success(
        data={"예측": formatted_pred},
        message="예측 성공"
    )

@router.get("/predict/test")
def budgetPredictionTest(current_user: User = Depends(get_current_user), db:Session = Depends(get_db)):
    preds, mae = training_and_prediction_test(db, current_user.userId)

    if not preds:
        return response_success(data={}, message="예측할 데이터가 부족합니다.")

    real_preds = expm1(preds)
    formatted_preds = f"{round(real_preds):,}원"
    return response_success(
        data = {
            "예측" : formatted_preds,
            "평가" : mae
            },
        message = "예측"
    )
