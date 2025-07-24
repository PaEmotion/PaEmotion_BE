from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

# 챌린지 생성 스키마
class ChallengeCreate(BaseModel):
    name: str
    publicityType: bool  
    password: Optional[str] = None
    challengeType: bool  
    goalCount: int  

# 챌린지 참여 스키마
class ChallengeJoin(BaseModel):
    password: Optional[str] = None

# 챌린지 리스트 조회 스키마
class ChallengeListRead(BaseModel):
    challengeId: int
    name: str
    challengeType: bool
    publicityType: bool
    createdDate: date
    currentMemberCount: int
    class Config: orm_mode = True

# 챌린지 단건 조회 스키마
class ChallengeRead(BaseModel):
    challengeId: int
    name: str
    publicityType: bool
    challengeType: bool
    createdDate: date
    goalCount: int
    isParticipating: Optional[bool] = False  
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

# 챌린지 상세 정보 조회 스키마
class ChallengeDetailRead(BaseModel):
    challengeId: int
    name: str
    publicityType: bool
    challengeType: bool
    createdDate: date
    goalCount: int
    teamProgressRate: float 
    members: List[ChallengeMemberRead]
    class Config: orm_mode = True