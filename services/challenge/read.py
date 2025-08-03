from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeListRead, ChallengeRead
from services.challenge.validate import ChallengeValidateService

class ChallengeReadService:
    
    def read_challenges_list(db: Session) -> List[ChallengeListRead]:

        current_date = datetime.now()

        # 모든 챌린지 정보 + 해당 챌린지 참여자 수 조회
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .group_by(Challenge.challengeId)
            .all()
        )

        # 기간이 유효한 챌린지만 필터링하여 리스트에 추가
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

        return challenges_list

    @staticmethod
    def read_challenge(db: Session, challenge_id: int) -> ChallengeRead:

        current_date = datetime.now()
        challenge = ChallengeValidateService.validate_challenge(db, challenge_id)

        end_date = challenge.createdDate + timedelta(days=6) 
        if end_date < current_date:
            raise HTTPException(status_code=400, detail="챌린지 기간이 종료되었습니다.")

        participants_count = (
            db.query(ChallengeParticipant)
            .filter(ChallengeParticipant.challengeId == challenge_id)
            .count()
        )

        return ChallengeRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            endDate=end_date,
            goalCount=challenge.goalCount,
            participantCount=participants_count,
        )

    @staticmethod
    def search_challenge(db: Session, query: str) -> List[ChallengeListRead]:

        current_date = datetime.now()

        # 검색어 포함 + 챌린지 기간 유효한 챌린지와 참여자 수 조회 쿼리 실행
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

        # 검색 결과 시 유효한 챌린지를 리스트에 추가
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

        return challenges_list


    @staticmethod
    def read_current_challenge(db: Session, user_id: int) -> int:
        current_date = datetime.now()

        # 현재 참여 중인 챌린지 조회 (기간 내)
        participant = (
            db.query(ChallengeParticipant)
            .join(Challenge)
            .filter(
                ChallengeParticipant.userId == user_id,
                Challenge.createdDate <= current_date,
                Challenge.createdDate + timedelta(days=6) >= current_date,
            )
            .first()
        )

        if not participant:
            raise HTTPException(status_code=404, detail="현재 참여 중인 챌린지가 없습니다.")

        return participant.challengeId
