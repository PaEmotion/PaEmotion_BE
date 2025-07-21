from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from sqlalchemy.orm import Session
from datetime import date

from db.session import get_db
from schemas.budget import (BudgetCreate, BudgetEdit, BudgetRead, LastSpentRead)
from services.budget import BudgetService

router = APIRouter(prefix="/budget", tags=["budget"])

# 예산 등록 라우터
@router.post("/create/{userId}")
def budget_create(
    userId: int = Path(...),
    budgetData: BudgetCreate = Body(...),
    db: Session = Depends(get_db)
):
    return BudgetService.budget_create(db, userId, budgetData)

# 예산 조회 라우터
@router.get("/{userId}", response_model=BudgetRead)
def budget_read(
    userId: int = Path(...),
    budgetMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.budget_read(db, userId, budgetMonth)

# 예산 수정 라우터
@router.put("/edit/{userId}")
def budget_edit(
    userId: int = Path(...),
    budgetMonth: date = Query(...),
    budgetData: BudgetEdit = Body(...),
    db: Session = Depends(get_db)
):
    return BudgetService.budget_edit(db, userId, budgetMonth, budgetData)

# 예산 전체 삭제
@router.delete("/delete/{userId}")
def budget_all_delete(
    userId: int = Path(...),
    budgetMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    BudgetService.budget_all_delete(db, userId, budgetMonth)
    return {"detail": "예산이 삭제되었습니다."}

# 예산 카테고리별 삭제
@router.delete("/delete/{userId}/{categoryBudgetId}")
def budget_category_delete(
    categoryBudgetId: int = Path(...),
    db: Session = Depends(get_db)
):
    BudgetService.budget_category_delete(db, categoryBudgetId)
    return {"detail": "카테고리별 예산이 삭제되었습니다."}

# 지난 달 소비 금액 조회 라우터
@router.get("/lastspent/{userId}", response_model=LastSpentRead)
def last_spent_read(
    userId: int = Path(...),
    lastMonth: date = Query(...),
    db: Session = Depends(get_db)
):
    return BudgetService.last_spent_read(db, userId, lastMonth)