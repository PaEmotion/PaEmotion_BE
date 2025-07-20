from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from typing import Optional
from models.record import Record
from models.budget import TotalBudget, CategoryBudget
import pandas as pd


# 예산 예측 모델 데이터 로드 함수, DataFrame 형태로 반환
def budget_data_read(db: Session, user_id: int, spend_date: Optional[str] = None) -> pd.DataFrame:
   
    query = db.query(Record).filter(Record.userId == user_id)
    if spend_date:
        query = query.filter(func.date(Record.spendDate) == spend_date)

    records = query.all()

    if not records:
        return pd.DataFrame()

    data = [{
        'userId': r.userId,
        'spendCost': r.spendCost,
        'spendDate': r.spendDate,
        'spendCategoryId' : r.spendCategoryId,
        'spendId':r.spendId
    } for r in records]

    df = pd.DataFrame(data)
    return df

# 타입 분류 모델 데이터 로드 함수, DataFrame 형태로 반환
def type_data_read(db: Session, user_id: int, spend_date: Optional[str] = None) -> pd.DataFrame:
    # 1) 기본 소비 기록 + emotionCategoryId 가져오기
    query = db.query(
        Record.userId,
        Record.spendCost,
        Record.spendDate,
        Record.spendCategoryId,
        Record.emotionCategoryId,
    ).filter(Record.userId == user_id)

    if spend_date:
        query = query.filter(func.date(Record.spendDate) == spend_date)

    records = query.all()
    if not records:
        return pd.DataFrame()

    data = [dict(
        userId=r.userId,
        spendCost=r.spendCost,
        spendDate=r.spendDate,
        spendCategoryId=r.spendCategoryId,
        emotionCategoryId=r.emotionCategoryId,
    ) for r in records]

    df = pd.DataFrame(data)

    # 2) TotalBudget 최신 예산 가져오기
    total_budget = db.query(TotalBudget).filter(TotalBudget.userId == user_id).order_by(TotalBudget.budgetMonth.desc()).first()

    if not total_budget:
        # 예산 데이터가 없으면 빈 리스트로 채우기
        df['budgets'] = '[]'
        df['actuals'] = '[]'
        return df

    # 3) CategoryBudget에서 예산 리스트 생성 (spendCategoryId 순서대로)
    category_budgets = db.query(CategoryBudget).filter(CategoryBudget.totalBudgetId == total_budget.totalBudgetId).order_by(CategoryBudget.spendCategoryId).all()
    budgets_list = [cb.amount for cb in category_budgets]

    # 4) 실제 소비 카테고리별 합산
    actuals_query = db.query(
        Record.spendCategoryId,
        func.sum(Record.spendCost).label('total_spent')
    ).filter(Record.userId == user_id).group_by(Record.spendCategoryId).order_by(Record.spendCategoryId).all()

    actuals_list = [0] * len(budgets_list)
    for rec in actuals_query:
        idx = rec.spendCategoryId - 1
        if 0 <= idx < len(actuals_list):
            actuals_list[idx] = rec.total_spent

    # 5) 문자열로 리스트 컬럼 추가
    df['budgets'] = str(budgets_list)
    df['actuals'] = str(actuals_list)

    return df
