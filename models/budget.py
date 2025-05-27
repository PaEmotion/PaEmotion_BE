from sqlalchemy import (
    Column, BigInteger, DateTime, PrimaryKeyConstraint, ForeignKey
)
from sqlalchemy.orm import relationship
from db.base import Base

class Budget(Base):
    __tablename__ = "budget"
    __table_args__ = (
        PrimaryKeyConstraint("budgetMonth", "userId"),
    )

    budgetMonth = Column(DateTime, nullable=False)
    userId = Column(BigInteger, ForeignKey("user.userId"), nullable=False)
    budgetMoney = Column(BigInteger, nullable=False)

    user = relationship("User", back_populates="budgets")
