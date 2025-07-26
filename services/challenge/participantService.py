from sqlalchemy.orm import Session
from typing import List

from models.challenge import ChallengeParticipant

## 챌린지 참여자 목록 조회 함수 ##
class ChallegeParticipantService:

    @staticmethod
    def read_participants(db: Session, challenge_id: int) -> List[ChallengeParticipant]:
        return db.query(ChallengeParticipant).filter_by(challengeId=challenge_id).all()