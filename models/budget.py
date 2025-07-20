from sqlalchemy import Column, BigInteger, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base

class TotalBudget(Base):
    __tablename__ = 'total_budget'

    totalBudgetId = Column(BigInteger, primary_key=True, autoincrement=True)
    userId = Column(BigInteger, ForeignKey("user.userId"), nullable=False)
    budgetMonth = Column(Date, nullable=False)
    totalAmount = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('userId', 'budgetMonth', name='uniq_user_month'),
    )

    user = relationship("User", back_populates="total_budgets")
    category_budgets = relationship("CategoryBudget", back_populates="total_budget", cascade="all, delete-orphan")


class CategoryBudget(Base):
    __tablename__ = 'category_budget'

    categoryBudgetId = Column(BigInteger, primary_key=True, autoincrement=True)
    totalBudgetId = Column(BigInteger, ForeignKey("total_budget.totalBudgetId", ondelete='CASCADE'), nullable=False)
    spendCategoryId = Column(BigInteger, ForeignKey("spend_category.spendCategoryId"), nullable=False)
    amount = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('totalBudgetId', 'spendCategoryId', name='uniq_total_category'),
    )

    total_budget = relationship("TotalBudget", back_populates="category_budgets")
    spend_category = relationship("SpendCategory")
