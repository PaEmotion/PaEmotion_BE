from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date
import re

# 챌린지 생성 스키마
class ChallengeCreate(BaseModel):
    name: str
    publicityType: bool  
    password: Optional[str] = None
    challengeType: bool  
    goalCount: int  

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상으로 입력해 주세요.')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('영어가 최소 1개 포함되어야 합니다.')
        if not re.search(r'\d', v):
            raise ValueError('숫자가 최소 1개 포함되어야 합니다.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('특수문자가 최소 1개 포함되어야 합니다.')
        return v

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
    endDate: date
    participantCount: int
    class Config: orm_mode = True

# 챌린지 단건 조회 스키마
class ChallengeRead(ChallengeListRead):
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
    endDate: date
    goalCount: int
    guineaFeedCurrent: int
    teamProgressRate: float 
    members: List[ChallengeMemberRead]
    class Config: orm_mode = True
