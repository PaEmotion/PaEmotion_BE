from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import date

from models.budget import TotalBudget, CategoryBudget
from models.record import Record
from schemas.budget import (BudgetCreate, BudgetEdit, BudgetRead,CategoryBudgetBase, CategorySpentBase, LastSpentRead)

class BudgetService:

    ## 예산 등록 함수
    @staticmethod
    def budget_create(db: Session, user_id: int, budget_data: BudgetCreate):
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
    def budget_read(db: Session, user_id: int, budget_month: date) -> BudgetRead:
        
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

    ## 예산 수정 함수
    @staticmethod
    def budget_edit(db: Session, user_id: int, budget_month: date, edited_data: BudgetEdit):

        # 1. 수정할 총 예산 데이터 조회
        total_budget = db.query(TotalBudget).filter_by(
            userId=user_id, budgetMonth=budget_month
        ).first()

        if not total_budget:
            raise HTTPException(status_code=404, detail="예산이 존재하지 않습니다.")

        # 2. 카테고리별 예산 수정/추가
        for edited_category_budget in edited_data.categoryBudget:
            if edited_category_budget.amount == 0:
                raise HTTPException(status_code=400, detail="예산 금액은 0원 이상이어야 합니다.")
    
            target_category_budget = db.query(CategoryBudget).filter_by(
                totalBudgetId=total_budget.totalBudgetId,
                spendCategoryId=edited_category_budget.spendCategoryId
            ).first()

            if target_category_budget:  # 기존 항목 수정
                target_category_budget.amount = edited_category_budget.amount 
            else:  # 없던 항목이면 추가
                new_category_budget = CategoryBudget(
                    totalBudgetId=total_budget.totalBudgetId,
                    spendCategoryId=edited_category_budget.spendCategoryId,
                    amount=edited_category_budget.amount
                )
                db.add(new_category_budget)
                db.flush()  # 새로 추가된 항목이 즉시 반영되도록 flush 호출

        # 3. 총 예산 계산
        category_budget_list = db.query(CategoryBudget).filter_by(
            totalBudgetId=total_budget.totalBudgetId
        ).all()
        total_budget.totalAmount = sum(category_budget.amount or 0 for category_budget in category_budget_list)

        # 4. 커밋
        db.commit()

        # 5. 수정된 예산 반환
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

    ## 예산 전체 삭제 함수
    @staticmethod
    def budget_all_delete(db: Session, user_id: int, budget_month: date):

        # 1. 총 예산 조회
        total_budget = db.query(TotalBudget).filter_by(
            userId=user_id,
            budgetMonth=budget_month
        ).first()

        if not total_budget:
            raise HTTPException(status_code=404, detail="예산이 존재하지 않습니다.")

        # 2. 예산 전체 삭제
        db.query(CategoryBudget).filter_by(
            totalBudgetId=total_budget.totalBudgetId
        ).delete()
        db.delete(total_budget)
        
        #3. 커밋
        db.commit()

    ## 예산 카테고리별 삭제 함수
    @staticmethod
    def budget_category_delete(db: Session, category_budget_id: int):

        # 1. 삭제할 카테고리 예산 조회
        target_category_budget = db.query(CategoryBudget).filter_by(
            categoryBudgetId=category_budget_id
        ).first()

        if not target_category_budget:
            raise HTTPException(status_code=404, detail="카테고리별 예산이 존재하지 않습니다.")

        # 2. 해당 카테고리 예산 삭제
        db.delete(target_category_budget)
        db.flush()

        # 3. 총예산 다시 계산
        total_budget = db.query(TotalBudget).filter_by(
            totalBudgetId=target_category_budget.totalBudgetId
        ).first()

        category_budget_list = db.query(CategoryBudget).filter_by(
            totalBudgetId=total_budget.totalBudgetId
        ).all()

        total_budget.totalAmount = sum(category_budget.amount or 0 for category_budget in category_budget_list)

        # 4. 커밋
        db.commit()

    ## 지난 달 소비 금액 조회 함수
    @staticmethod
    def last_spent_read(db: Session, user_id: int, last_month: date) -> LastSpentRead:

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
