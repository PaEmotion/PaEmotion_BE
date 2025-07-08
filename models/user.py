from sqlalchemy import (
    Column, BigInteger, String, Boolean
)
from sqlalchemy.orm import relationship
from db.base import Base

class User(Base):
    __tablename__ = 'user'

    userId = Column('userId', BigInteger, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

    # User가 가진 여러 관계 전부 다 넣기
    records = relationship('Record', back_populates='user')
    monthlyReports = relationship("AdminMonthlyReport", back_populates="user")
    weeklyReports = relationship("AdminWeeklyReport", back_populates="user")
    adminDailyReports = relationship("AdminDailyReport", back_populates="user")
    userReports = relationship("UserReport", back_populates="user")
    budgets = relationship("Budget", back_populates="user")