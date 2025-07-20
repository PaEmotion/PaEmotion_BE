from fastapi import APIRouter, Depends
from services.ml.budget import training_and_prediction
from sqlalchemy.orm import Session
from db.session import get_db

router = APIRouter(prefix="/ml")

@router.get("/predict/{userId}")
def budgetPrediction(userId:int, db: Session = Depends(get_db)):
    y_pred = training_and_prediction(db, userId)
    return {"예측" : y_pred}