from sqlalchemy.orm import Session
from fastapi import HTTPException

from models.challenge import Challenge

class ChallengeValidateService:

    @staticmethod
    def validate_challenge(db: Session, challenge_id: int) -> Challenge:
        challenge = db.query(Challenge).filter_by(challengeId=challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        return challenge