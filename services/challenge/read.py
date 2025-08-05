from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeListRead, ChallengeRead

class ChallengeReadService:

    # 목록 조회
    @staticmethod 
    def read_challenges_list(db: Session) -> List[ChallengeListRead]:

        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = func.date_add(func.date(Challenge.createdDate), text('INTERVAL 7 DAY'))

        # 유효기간 내의 모든 챌린지 정보 + 해당 챌린지 참여자 수 조회 쿼리
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .filter(
                end_date > today_date
            )
            .group_by(Challenge.challengeId)
            .all()
        )

        challenges_list = []
        for challenge, participants_count in results:
            end_date = challenge.createdDate.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)
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

    # 단건 조회
    @staticmethod
    def read_challenge(db: Session, challenge_id: int) -> ChallengeRead:

        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = func.date_add(func.date(Challenge.createdDate), text('INTERVAL 7 DAY'))

        challenge = (
            db.query(Challenge)
            .filter(
                Challenge.challengeId == challenge_id,
                end_date > today_date
            )
            .first()
        )
        if not challenge:
            raise HTTPException(status_code=400, detail="챌린지 기간이 종료되었거나 존재하지 않습니다.")

        end_date = challenge.createdDate.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)

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

    # 검색 조회
    @staticmethod
    def search_challenge(db: Session, query: str) -> List[ChallengeListRead]:

        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = func.date_add(func.date(Challenge.createdDate), text('INTERVAL 7 DAY'))
        
         # 검색어 포함 + 기간 유효한 챌린지 + 참여자 수 조회 쿼리
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .filter(
                Challenge.name.ilike(f"%{query}%"),
                end_date > today_date
            )
            .group_by(Challenge.challengeId)
            .all()
        )

        challenges_list = []
        for challenge, participants_count in results:
            end_date = challenge.createdDate.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)
            challenges_list.append(
                ChallengeListRead(
                    challengeId=challenge.challengeId,
                    name=challenge.name,
                    challengeType=challenge.challengeType,
                    publicityType=challenge.publicityType,
                    endDate=end_date,
                    goalCount=challenge.goalCount,
                    participantCount=participants_count,
                )
            )

        return challenges_list

    # 현재 참여중인 챌린지 아이디 조회 (기간 내)
    @staticmethod
    def read_current_challenge(db: Session, user_id: int) -> int:

        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = func.date_add(func.date(Challenge.createdDate), text('INTERVAL 7 DAY'))

        participant = (
            db.query(ChallengeParticipant)
            .join(Challenge)
            .filter(
                ChallengeParticipant.userId == user_id,
                Challenge.createdDate <= datetime.now(),
                end_date > today_date
            )
            .first()
        )

        if not participant:
            raise HTTPException(status_code=404, detail="현재 참여 중인 챌린지가 없습니다.")

        return participant.challengeId