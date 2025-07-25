from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import date

from models.budget import TotalBudget, CategoryBudget
from models.record import Record
from schemas.budget import (BudgetCreate, BudgetRead,CategoryBudgetBase, CategorySpentBase, LastSpentRead)

class BudgetService:

    ## 예산 등록 함수
    @staticmethod
    def create_budgets(db: Session, user_id: int, budget_data: BudgetCreate):
        # 1. 카테고리별 예산의 합으로 총 예산 계산
        total_amount = sum(category_budget.amount or 0 for category_budget in budget_data.categoryBudget)

        # 2. 총 예산 등록
        new_total_budget = TotalBudget(
            userId=user_id,
            budgetMonth=budget_data.budgetMonth,
            totalAmount=total_amount 
        )
        db.add(new_total_budget)
        db.flush()  

        # 3. 카테고리별 예산 등록
        category_budget_list = []
        for category_budget in budget_data.categoryBudget:
            new_category_budget = CategoryBudget(
                totalBudgetId=new_total_budget.totalBudgetId,
                spendCategoryId=category_budget.spendCategoryId,
                amount=category_budget.amount
            )
            db.add(new_category_budget)
            category_budget_list.append(new_category_budget)

        # 4. 커밋
        db.commit()

        # 5. 등록한 예산 반환
        return BudgetRead(
            userId=new_total_budget.userId,
            totalBudgetId=new_total_budget.totalBudgetId,
            budgetMonth=new_total_budget.budgetMonth,
            totalAmount=new_total_budget.totalAmount,
            categoryBudget=[
                CategoryBudgetBase(
                    spendCategoryId=category_budget.spendCategoryId,
                    amount=category_budget.amount
                ) for category_budget in category_budget_list
            ]
        )

    ## 예산 조회 함수
    @staticmethod
    def read_budgets(db: Session, user_id: int, budget_month: date) -> BudgetRead:
        
        # 1. 총 예산 조회
        total_budget = db.query(TotalBudget).filter_by(
            userId=user_id,
            budgetMonth=budget_month
        ).first()

        if not total_budget:
            raise HTTPException(status_code=404, detail="예산이 존재하지 않습니다.")

        # 2. 카테고리별 예산 조회
        category_budget_list = db.query(CategoryBudget).filter_by(
            totalBudgetId=total_budget.totalBudgetId
        ).all()

        # 3. 조회한 예산 반환
        return BudgetRead(
            userId=total_budget.userId,
            totalBudgetId=total_budget.totalBudgetId,
            budgetMonth=total_budget.budgetMonth,
            totalAmount=total_budget.totalAmount,
            categoryBudget=[
                CategoryBudgetBase(
                    spendCategoryId=category_budget.spendCategoryId,
                    amount=category_budget.amount
                ) for category_budget in category_budget_list
            ]
        )

    ## 지난 달 소비 금액 조회 함수
    @staticmethod
    def read_last_spent(db: Session, user_id: int, last_month: date) -> LastSpentRead:

        # 1. 해당 유저, 해당 월의 총 소비 금액 합계 조회
        total_spent = db.query(func.sum(Record.spendCost)).filter(
            Record.userId == user_id,
            func.date_format(Record.spendDate, "%Y-%m") == last_month.strftime("%Y-%m")
        ).scalar() or 0

        # 2. 해당 유저, 해당 월의 카테고리별 소비 금액 합계 조회 (그룹핑)
        category_spent = db.query(
            Record.spendCategoryId,
            func.sum(Record.spendCost).label("spendCost")
        ).filter(
            Record.userId == user_id,
            func.date_format(Record.spendDate, "%Y-%m") == last_month.strftime("%Y-%m")
        ).group_by(Record.spendCategoryId).all()

        # 3. 결과 반환
        return LastSpentRead(
            userId=user_id,
            lastMonth=last_month,
            totalSpent=total_spent,
            categorySpent=[
                CategorySpentBase(
                    spendCategoryId=row.spendCategoryId,
                    spent=row.spendCost
                ) for row in category_spent
            ]
        )