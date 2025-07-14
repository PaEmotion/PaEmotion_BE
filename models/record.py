from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base

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