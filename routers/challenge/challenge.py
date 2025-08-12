from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.session import get_db
from schemas.challenge import (ChallengeCreate, ChallengeJoin, ChallengeIdRead, 
    ChallengeListRead, ChallengeRead, ChallengeDetailRead)
from services.challenge.basic import ChallengeBasicService
from services.challenge.read import ChallengeReadService
from services.challenge.detail import ChallengeDetailService
from auth.jwt_token import get_current_user 
from utils.response import response_success

router = APIRouter(prefix="/challenges", tags=["challenges"])

@router.post("/create", status_code=201)
def create_challenge(
    challenge_data: ChallengeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) 
):
    challenge_id = ChallengeBasicService.create_challenge(db, current_user.userId, challenge_data)
    return response_success(
        data = {"challenge_id" : challenge_id },
        message = "챌린지 생성 완료",
        status_code=201
    )

@router.post("/join", status_code=200)
def join_challenge(
    join_data: ChallengeJoin,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    challenge_id = ChallengeBasicService.join_challenge(db, current_user.userId, join_data)
    return response_success(
        data = {"challenge_id" : challenge_id },
        message = "챌린지 참여 완료"
    )

@router.get("/search", response_model=List[ChallengeListRead])
def search_challenge(
    name: str,
    db: Session = Depends(get_db)
):
    result = ChallengeReadService.search_challenge(db, name)

    if not result:
        return response_success(
            data = [],
            message="검색 결과가 없습니다."
        )
    return response_success(data=result, message="검색 결과 반환 완료")

@router.get("/current", response_model=ChallengeIdRead)
def read_current_challenge(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    challenge_id = ChallengeReadService.read_current_challenge(db, current_user.userId)
    return response_success(
        data = {"challenge_id" : challenge_id },
        message = "참여중인 챌린지 조회 완료"
    )

@router.get("", response_model=List[ChallengeListRead])
def read_challenges_list(
    db: Session = Depends(get_db)
):
    result = ChallengeReadService.read_challenges_list(db)
    return response_success(
        data = result,
        message = "챌린지 목록 조회 완료"
    )

@router.get("/{challengeId}", response_model=ChallengeRead)
def read_challenge(
    challengeId: int,
    db: Session = Depends(get_db)
):
    result = ChallengeReadService.read_challenge(db, challengeId)
    return response_success(
        data = result,
        message = "챌린지 단건 조회 완료"
    )

@router.get("/detail/{challengeId}", response_model=ChallengeDetailRead)
def read_challenge_detail(
    challengeId: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = ChallengeDetailService.read_challenge_detail(db, challengeId, current_user.userId)
    return response_success(
        data = result,
        message = "챌린지 상세 조회 완료"
    )