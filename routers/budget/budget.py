from fastapi import APIRouter, Depends, Path, Query, Body
from sqlalchemy.orm import Session
from datetime import date
from auth.jwt_token import get_current_user
from db.session import get_db
from schemas.budget import (BudgetCreate, BudgetRead, LastSpentRead)
from services.budget.budget import BudgetService
from models.user import User
from utils.response import response_success

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/create")
def create_budgets(
    current_user : User = Depends(get_current_user),
    budgetData: BudgetCreate = Body(...),
    db: Session = Depends(get_db)
):
    result = BudgetService.create_budgets(db, current_user.userId, budgetData)
    return response_success(data=result, message="예산 생성 완료", status_code=201)

@router.get("/me", response_model=BudgetRead)
def read_budgets(
    current_user : User = Depends(get_current_user),
    budgetMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    result = BudgetService.read_budgets(db, current_user.userId, budgetMonth)
    return response_success(data=result, message="예산 조회 완료")

@router.get("/lastspent/me", response_model=LastSpentRead)
def read_last_spent(
    current_user : User = Depends(get_current_user),
    lastMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    result = BudgetService.read_last_spent(db, current_user.userId, lastMonth)
    return response_success(data=result, message="지난 예산 조회 완료")