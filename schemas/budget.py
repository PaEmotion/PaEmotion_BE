from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

# 카테고리별 예산
class CategoryBudgetBase(BaseModel):
    spendCategoryId: int = Field(...)
    amount: Optional[int] = Field(None)

# 지난달 카테고리별 소비 금액
class CategorySpentBase(BaseModel):  
    spendCategoryId: int = Field(...)
    spent: Optional[int] = Field(None)

# 예산 등록 스키마
class BudgetCreate(BaseModel):
    budgetMonth: date = Field(...)
    categoryBudget: List[CategoryBudgetBase] = Field(...) 

# 예산 조회 스키마
class BudgetRead(BaseModel):
    userId: int
    totalBudgetId: int
    budgetMonth: date = Field(...)
    totalAmount: int = Field(...)
    categoryBudget: List[CategoryBudgetBase] = Field(...)
    class Config: orm_mode = True

# 지난달 소비 금액 조회 스키마
class LastSpentRead(BaseModel): 
    userId: int
    lastMonth: date = Field(...)
    totalSpent: int = Field(...)
    categorySpent: List[CategorySpentBase] = Field(...)
    class Config: orm_mode = True