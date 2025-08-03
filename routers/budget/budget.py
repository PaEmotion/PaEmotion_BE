from fastapi import APIRouter, Depends, Path, Query, Body
from sqlalchemy.orm import Session
from datetime import date

from db.session import get_db
from schemas.budget import (BudgetCreate, BudgetRead, LastSpentRead)
from services.budget.budget import BudgetService

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.post("/create/{userId}")
def create_budgets(
    userId: int = Path(...),
    budgetData: BudgetCreate = Body(...),
    db: Session = Depends(get_db)
):
    return BudgetService.create_budgets(db, userId, budgetData)

@router.get("/{userId}", response_model=BudgetRead)
def read_budgets(
    userId: int = Path(...),
    budgetMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.read_budgets(db, userId, budgetMonth)

@router.get("/lastspent/{userId}", response_model=LastSpentRead)
def read_last_spent(
    userId: int = Path(...),
    lastMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.read_last_spent(db, userId, lastMonth)