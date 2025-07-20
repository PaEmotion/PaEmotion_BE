from fastapi import APIRouter, Depends, HTTPException, Query
from services.ml.type import classify_type
from sqlalchemy.orm import Session
from db.session import get_db

router = APIRouter(prefix="/ml")

@router.get("/classify/{userId}")
def typeClassification(
    userId: int,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db)
):
    pred_labels = classify_type(db, userId, year, month)
    if not pred_labels:
        raise HTTPException(status_code=404, detail="조회된 데이터가 없습니다.")
    return pred_labels