from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeListRead, ChallengeRead
from services.challenge.validateService import ChallengeValidateService

class ChallengeReadService:
    
    ## 챌린지 목록 조회 함수 ##
    def read_challenges_list(db: Session) -> List[ChallengeListRead]:

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 모든 챌린지 정보 + 해당 챌린지 참여자 수 조회
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .group_by(Challenge.challengeId)
            .all()
        )

        # 3. 기간이 유효한 챌린지만 필터링하여 리스트에 추가
        challenges_list = []
        for challenge, participants_count in results:
            end_date = challenge.createdDate + timedelta(days=6)  
            if end_date >= current_date:
                challenges_list.append(
                    ChallengeListRead(
                        challengeId=challenge.challengeId,
                        name=challenge.name,
                        publicityType=challenge.publicityType,
                        challengeType=challenge.challengeType,
                        endDate=end_date,
                        goalCount=challenge.goalCount,
                        participantCount=participants_count,
                    )
                )

        # 4. 결과 반환 
        return challenges_list

    ##  챌린지 단건 조회 함수 ##
    @staticmethod
    def read_challenge(db: Session, challenge_id: int) -> ChallengeRead:

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 챌린지 유효성 검증 및 조회
        challenge = ChallengeValidateService.validate_challenge(db, challenge_id)

        # 3. 종료된 챌린지면 예외 반환
        end_date = challenge.createdDate + timedelta(days=6) 
        if end_date < current_date:
            raise HTTPException(status_code=400, detail="챌린지 기간이 종료되었습니다.")

        # 4. 참여자 수 조회
        participants_count = (
            db.query(ChallengeParticipant)
            .filter(ChallengeParticipant.challengeId == challenge_id)
            .count()
        )

        # 5. 결과 반환
        return ChallengeRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            endDate=end_date,
            goalCount=challenge.goalCount,
            participantCount=participants_count,
        )

    ## 챌린지 검색 함수 ##
    @staticmethod
    def search_challenge(db: Session, query: str) -> List[ChallengeListRead]:

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 검색어 포함 + 챌린지 기간 유효한 챌린지와 참여자 수 조회 쿼리 실행
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .filter(
                Challenge.name.ilike(f"%{query}%"),
                (Challenge.createdDate + timedelta(days=7)) > current_date,
            )
            .group_by(Challenge.challengeId)
            .all()
        )

        # 3. 검색 결과 시 유효한 챌린지를 리스트에 추가
        challenges_list = []
        for challenge, participants_count in results:
            challenges_list.append(
                ChallengeListRead(
                    challengeId=challenge.challengeId,
                    name=challenge.name,
                    challengeType=challenge.challengeType,
                    publicityType=challenge.publicityType,
                    endDate=(challenge.createdDate + timedelta(days=7)),
                    goalCount = challenge.goalCount,
                    participantCount=participants_count,
                )
            )

        # 4. 결과 반환
        return challenges_list
