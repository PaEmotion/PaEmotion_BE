from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from schemas.validator import validate_password

class ChallengeCreate(BaseModel):
    name: str
    publicityType: bool  
    password: Optional[str] = None
    challengeType: bool  
    goalCount: int  

    @field_validator('password')
    @classmethod
    def validate_password(cls, v:Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return validate_password(v)

class ChallengeJoin(BaseModel):
    challengeId: int
    password: Optional[str] = None

# 현재 참여중인 챌린지 아이디 조회
class ChallengeIdRead(BaseModel):
    challengeId: int

class ChallengeListRead(BaseModel):
    challengeId: int
    name: str
    challengeType: bool
    publicityType: bool
    endDate: datetime
    goalCount: int
    participantCount: int
    class Config: orm_mode = True

class ChallengeRead(ChallengeListRead):
    class Config: orm_mode = True

class ChallengeSearch(ChallengeListRead):
    class Config: orm_mode = True

# 챌린지 멤버 조회
class ChallengeMemberRead(BaseModel):
    userId: int
    isHost: bool
    contributionRate: float
    class Config: orm_mode = True

class ChallengeMemberContribution(BaseModel):
    userId: int
    isHost: bool
    spendCount: int
    contributionRate: float
    class Config:
        orm_mode = True

class ChallengeTeamProgress(BaseModel):
    teamProgressRate: float
    guineaFeedCount: int

class ChallengeDetailRead(BaseModel):
    challengeId: int
    name: str
    publicityType: bool
    challengeType: bool
    endDate: datetime
    goalCount: int
    guineaFeedCurrent: int
    teamProgressRate: float 
    participantsInfo: List[ChallengeMemberRead]
    class Config: orm_mode = True
