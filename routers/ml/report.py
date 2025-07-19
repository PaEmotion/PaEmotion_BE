from fastapi import APIRouter, Depends
from services.ml.report import train_and_prediction

router = APIRouter()

@router.get("/ml/predict/{userId}")
def budgetPrediction(userId:int):
    y_pred = train_and_prediction(userId)
    return {"예측" : y_pred}