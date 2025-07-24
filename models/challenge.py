from sqlalchemy import Column, BigInteger, Boolean, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from db.session import Base

class Challenge(Base):
    __tablename__ = "challenge"

    challengeId = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    publicityType = Column(Boolean, nullable=False)  
    password = Column(String(255), nullable=True)  
    challengeType = Column(Boolean, nullable=False)  
    goalCount = Column(Integer, nullable=False)  
    createdAt = Column(DateTime(timezone=True), server_default=func.now())  

class ChallengeParticipant(Base):
    __tablename__ = "challenge_participant"

    challengeId = Column(BigInteger, ForeignKey("challenge.challengeId", ondelete="CASCADE"), primary_key=True)
    userId = Column(BigInteger, ForeignKey("user.userId", ondelete="CASCADE"), primary_key=True)

    isHost = Column(Boolean, nullable=False)  

    challenge = relationship("Challenge", back_populates="participants")
    user = relationship("User", back_populates="challengeParticipants")