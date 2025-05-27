from sqlalchemy import Column, BigInteger, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from db.base import Base

class AdminDailyReport(Base):
    __tablename__ = "admin_daily_report"
    __table_args__ = (
        PrimaryKeyConstraint("userId", "recordDate", "emotionCategoryId"),
    )

    userId = Column("userId", BigInteger, ForeignKey("user.userId"), nullable=False)
    recordDate = Column("recordDate", DateTime, nullable=False)
    emotionCategoryId = Column("emotionCategoryId", BigInteger, ForeignKey("emotion_category.emotionCategoryId"), nullable=False)
    spendCount = Column("spendCount", Integer, nullable=False)
    totalSpend = Column("totalSpend", BigInteger, nullable=False)

    user = relationship("User", back_populates="adminDailyReports")
    emotionCategory = relationship("EmotionCategory", back_populates="adminDailyReports")

class AdminMonthlyReport(Base):
    __tablename__ = "admin_monthly_report"
    __table_args__ = (
        PrimaryKeyConstraint('userId', 'recordDate', 'emotionCategoryId', 'spendCategoryId'),
    )

    userId = Column(BigInteger, ForeignKey('user.userId'), nullable=False)
    recordDate = Column(DateTime, nullable=False)
    emotionCategoryId = Column(BigInteger, ForeignKey('emotion_category.emotionCategoryId'), nullable=False)
    spendCategoryId = Column(BigInteger, ForeignKey('spend_category.spendCategoryId'), nullable=False)
    spendCount = Column(Integer, nullable=False)
    totalSpend = Column(BigInteger, nullable=False)

    user = relationship("User", back_populates="monthlyReports")
    emotionCategory = relationship("EmotionCategory")
    spendCategory = relationship("SpendCategory")

class AdminWeeklyReport(Base):
    __tablename__ = "admin_weekly_report"
    __table_args__ = (
        PrimaryKeyConstraint('userId', 'recordDate', 'emotionCategoryId', 'spendCategoryId'),
    )

    userId = Column(BigInteger, ForeignKey('user.userId'), nullable=False)
    recordDate = Column(DateTime, nullable=False)
    emotionCategoryId = Column(BigInteger, ForeignKey('emotion_category.emotionCategoryId'), nullable=False)
    spendCategoryId = Column(BigInteger, ForeignKey('spend_category.spendCategoryId'), nullable=False)
    spendCount = Column(Integer, nullable=False)
    totalSpend = Column(BigInteger, nullable=False)

    user = relationship("User", back_populates="weeklyReports")
    emotionCategory = relationship("EmotionCategory")
    spendCategory = relationship("SpendCategory")

import enum
from sqlalchemy import (
    Column, BigInteger, Date, Enum, Text, ForeignKey, PrimaryKeyConstraint
)

class ReportTypeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class UserReport(Base):
    __tablename__ = "userReport"
    __table_args__ = (
        PrimaryKeyConstraint("userId", "reportDate", "reportType"),
    )

    userId = Column(BigInteger, ForeignKey("user.userId"), nullable=False)
    reportDate = Column(Date, nullable=False)
    reportType = Column(Enum(ReportTypeEnum), nullable=False)
    reportText = Column(Text, nullable=False)

    user = relationship("User", back_populates="userReports")
