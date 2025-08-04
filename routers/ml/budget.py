from fastapi import APIRouter, Depends
from services.ml.budget import training_and_prediction
from sqlalchemy.orm import Session
from db.session import get_db
from utils.response import response_success
from models.user import User
from auth.jwt_token import get_current_user
router = APIRouter(prefix="/ml")

@router.get("/predict")
def budgetPrediction(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    y_pred = training_and_prediction(db, current_user.userId)
    return response_success(
        data = {"예측" : y_pred},
        message = "예측"
    )