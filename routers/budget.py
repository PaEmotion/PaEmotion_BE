from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session
from datetime import date

from db.session import get_db
from schemas.budget import (BudgetCreate, BudgetRead, LastSpentRead)
from services.budget import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])

# 예산 등록 라우터 
@router.post("/create/{userId}")
def create_budgets(
    userId: int = Path(...),
    budgetData: BudgetCreate = Body(...),
    db: Session = Depends(get_db)
):
    return BudgetService.create_budgets(db, userId, budgetData)

# 예산 조회 라우터 (라우터로 유저아이디 받고, 쿼리파람으로 조회할 달 입력)
@router.get("/{userId}", response_model=BudgetRead)
def read_budgets(
    userId: int = Path(...),
    budgetMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.read_budgets(db, userId, budgetMonth)

# 지난 달 소비 금액 조회 라우터 (라우터로 유저아이디 받고, 쿼리파람으로 소비금액 조회할 달 입력)
@router.get("/lastspent/{userId}", response_model=LastSpentRead)
def read_last_spent(
    userId: int = Path(...),
    lastMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.read_last_spent(db, userId, lastMonth)