from sqlalchemy import (
    Column, BigInteger, Integer, DateTime, Date, Enum, Text, ForeignKey,
    PrimaryKeyConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
import enum
from db.base import Base

class AdminDailyReport(Base):
    __tablename__ = "admin_daily_report"
    __table_args__ = (
        PrimaryKeyConstraint("userId", "recordDate", "emotionCategoryId"),
    )

    userId = Column(BigInteger, ForeignKey("user.userId"), nullable=False)
    recordDate = Column(DateTime, nullable=False)
    emotionCategoryId = Column(BigInteger, ForeignKey("emotion_category.emotionCategoryId"), nullable=False)
    spendCount = Column(Integer, nullable=False)
    totalSpend = Column(BigInteger, nullable=False)

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


class ReportTypeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class UserReport(Base):
    __tablename__ = "user_report"
    __table_args__ = (
        UniqueConstraint("userId", "reportDate", "reportType", name="unique_user_report"),
    )

    reportId = Column(BigInteger, primary_key=True, autoincrement=True)
    userId = Column(BigInteger, ForeignKey("user.userId"), nullable=False)
    reportDate = Column(Date, nullable=False)
    reportType = Column(Enum("daily", "weekly", "monthly"), nullable=False)
    reportText = Column(Text, nullable=False)
    
    user = relationship("User", back_populates="userReports")
