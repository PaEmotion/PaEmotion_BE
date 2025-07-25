from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from db.session import get_db
from schemas.challenge import (ChallengeCreate, ChallengeJoin, ChallengeListRead, 
    ChallengeRead, ChallengeDetailRead)
from services.challenge import ChallengeService
from auth.jwt_token import get_current_user 

router = APIRouter(prefix="/challenges", tags=["challenges"])

# 챌린지 생성 라우터
@router.post("/create", status_code=201)
def create_challenge(
    challenge_data: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)  # User 객체 전체
):
    ChallengeService.create_challenge(db, current_user.userId, challenge_data)
    return {"message": "챌린지를 성공적으로 생성했습니다."}

# 챌린지 참여 라우터
@router.post("/join", status_code=200)
def join_challenge(
    join_data: ChallengeJoin,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    ChallengeService.join_challenge(db, current_user.userId, join_data)
    return {"message": "챌린지에 성공적으로 참여했습니다."}

# 챌린지 검색 라우터
@router.get("/search", response_model=List[ChallengeListRead])
def search_challenge(
    name: str,
    db: Session = Depends(get_db)
):
    result = ChallengeService.search_challenge(db, name)

    if not result:
        return JSONResponse(
            content={"message": "검색 결과가 없습니다.", "challenges": []},
            status_code=200
        )
    return result

# 챌린지 목록 조회 라우터
@router.get("", response_model=List[ChallengeListRead])
def read_challenges_list(
    db: Session = Depends(get_db)
):
    return ChallengeService.read_challenges_list(db)

# 챌린지 단건 조회 라우터
@router.get("/{challengeId}", response_model=ChallengeRead)
def read_challenge(
    challengeId: int,
    db: Session = Depends(get_db)
):
    return ChallengeService.read_challenge(db, challengeId)

# 챌린지 상세 정보 조회 라우터
@router.get("/detail/{challengeId}", response_model=ChallengeDetailRead)
def read_challenge_detail(
    challengeId: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return ChallengeService.read_challenge_detail(db, challengeId, current_user.userId)