from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from schemas.validator import validate_password

# 챌린지 생성 스키마
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

# 챌린지 참여 스키마
class ChallengeJoin(BaseModel):
    challengeId: int
    password: Optional[str] = None

# 챌린지 리스트 조회 스키마
class ChallengeListRead(BaseModel):
    challengeId: int
    name: str
    challengeType: bool
    publicityType: bool
    endDate: datetime
    goalCount: int
    participantCount: int
    class Config: orm_mode = True

# 챌린지 단건 조회 스키마
class ChallengeRead(ChallengeListRead):
    class Config: orm_mode = True

# 챌린지 검색 스키마
class ChallengeSearch(ChallengeListRead):
    class Config: orm_mode = True

# 챌린지 멤버 조회 스키마
class ChallengeMemberRead(BaseModel):
    userId: int
    isHost: bool
    contributionRate: float
    class Config: orm_mode = True

# 멤버별 소비 횟수 및 기여도 계산용 스키마
class ChallengeMemberContribution(BaseModel):
    userId: int
    isHost: bool
    spendCount: int
    contributionRate: float
    class Config:
        orm_mode = True

# 팀 전체 진행률 및 기니피그 먹이 계산용 스키마
class ChallengeTeamProgress(BaseModel):
    teamProgressRate: float
    guineaFeedCount: int

# 챌린지 상세 정보 조회 스키마
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
