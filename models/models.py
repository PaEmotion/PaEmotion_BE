import enum
from sqlalchemy import (
    Column, BigInteger, Integer, String, DateTime, Date, Text,
    ForeignKey, PrimaryKeyConstraint, Enum
)
from sqlalchemy.orm import relationship
from db.base import Base


# 1. Enum 정의
class ReportTypeEnum(enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


# 2. 참조 대상 먼저: EmotionCategory, SpendCategory, User
class EmotionCategory(Base):
    __tablename__ = 'emotion_category'

    emotionCategoryId = Column('emotionCategoryId', BigInteger, primary_key=True, nullable=False)
    emotionCategoryName = Column('emotionCategoryName', String(255), nullable=False)

    records = relationship('Record', back_populates='emotionCategory')
    adminDailyReports = relationship("AdminDailyReport", back_populates="emotionCategory")


class SpendCategory(Base):
    __tablename__ = 'spend_category'

    spendCategoryId = Column('spendCategoryId', BigInteger, primary_key=True, nullable=False)
    spendCategoryName = Column('spendCategoryName', String(255), nullable=False)

    records = relationship('Record', back_populates='spendCategory')


class User(Base):
    __tablename__ = 'user'

    userId = Column('userId', BigInteger, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    nickname = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)

    records = relationship('Record', back_populates='user')
    monthlyReports = relationship("AdminMonthlyReport", back_populates="user")
    weeklyReports = relationship("AdminWeeklyReport", back_populates="user")
    adminDailyReports = relationship("AdminDailyReport", back_populates="user")
    userReports = relationship("UserReport", back_populates="user")
    budgets = relationship("Budget", back_populates="user")


# 3. 참조하는 테이블들 정의

class Record(Base):
    __tablename__ = 'record'

    spendId = Column('spendId', BigInteger, primary_key=True, nullable=False)
    userId = Column('userId', BigInteger, ForeignKey('user.userId'), nullable=False)
    emotionCategoryId = Column('emotionCategoryId', BigInteger, ForeignKey('emotion_category.emotionCategoryId'), nullable=False)
    spendCategoryId = Column('spendCategoryId', BigInteger, ForeignKey('spend_category.spendCategoryId'), nullable=False)
    spendItem = Column('spendItem', String(255), nullable=False)
    spendCost = Column('spendCost', BigInteger, nullable=False)
    spendDate = Column('spendDate', DateTime, nullable=False)

    user = relationship('User', back_populates='records')
    emotionCategory = relationship('EmotionCategory', back_populates='records')
    spendCategory = relationship('SpendCategory', back_populates='records')


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


class Budget(Base):
    __tablename__ = "budget"
    __table_args__ = (
        PrimaryKeyConstraint("budgetMonth", "userId"),
    )

    budgetMonth = Column(DateTime, nullable=False)
    userId = Column(BigInteger, ForeignKey("user.userId"), nullable=False)
    budgetMoney = Column(BigInteger, nullable=False)

    user = relationship("User", back_populates="budgets")


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
