import enum
from sqlalchemy import Column, BigInteger, String
from sqlalchemy.orm import relationship
from db.base import Base

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
    category_budgets = relationship('CategoryBudget', back_populates='spend_category', 
        cascade='all, delete-orphan', passive_deletes=True)