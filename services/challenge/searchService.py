from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeListRead

## 챌린지 검색 함수 ##
class ChallengeSearchService:

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
                    endDate=(challenge.createdDate + timedelta(days=7)).date(),
                    participantCount=participants_count,
                )
            )

        # 4. 결과 반환
        return challenges_list