from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

class CategoryBudgetBase(BaseModel):
    spendCategoryId: int = Field(...)
    amount: Optional[int] = Field(None)

class CategorySpentBase(BaseModel):  
    spendCategoryId: int = Field(...)
    spent: Optional[int] = Field(None)

class BudgetCreate(BaseModel):
    budgetMonth: date = Field(...)
    categoryBudget: List[CategoryBudgetBase] = Field(...) 

class BudgetRead(BaseModel):
    userId: int
    totalBudgetId: int
    budgetMonth: date = Field(...)
    totalAmount: int = Field(...)
    categoryBudget: List[CategoryBudgetBase] = Field(...)
    class Config: orm_mode = True

class LastSpentRead(BaseModel): 
    userId: int
    lastMonth: date = Field(...)
    totalSpent: int = Field(...)
    categorySpent: List[CategorySpentBase] = Field(...)
    class Config: orm_mode = True