from fastapi import APIRouter, Depends, Path, Query, Body
from sqlalchemy.orm import Session
from datetime import date
from auth.jwt_token import get_current_user
from db.session import get_db
from schemas.budget import (BudgetCreate, BudgetRead, LastSpentRead)
from services.budget.budget import BudgetService
from models.user import User

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/create")
def create_budgets(
    current_user : User = Depends(get_current_user),
    budgetData: BudgetCreate = Body(...),
    db: Session = Depends(get_db)
):
    return BudgetService.create_budgets(db, current_user.userId, budgetData)

@router.get("/me", response_model=BudgetRead)
def read_budgets(
    current_user : User = Depends(get_current_user),
    budgetMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.read_budgets(db, current_user.userId, budgetMonth)

@router.get("/lastspent/me", response_model=LastSpentRead)
def read_last_spent(
    current_user : User = Depends(get_current_user),
    lastMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.read_last_spent(db, current_user.userId, lastMonth)