from fastapi import APIRouter
from services.ml.report import training_and_prediction

router = APIRouter()

@router.get("/ml/predict/{userId}")
def budgetPrediction(userId:int):
    y_pred = training_and_prediction(userId)
    return {"예측" : y_pred}