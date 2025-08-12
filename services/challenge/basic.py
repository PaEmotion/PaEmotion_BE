from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from datetime import datetime
from fastapi import HTTPException
from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeCreate, ChallengeJoin
from services.challenge.validate import ChallengeValidateService

class ChallengeBasicService:

    @staticmethod
    def create_challenge(db: Session, user_id: int, challenge_data: ChallengeCreate):

        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = func.date_add(func.date(Challenge.createdDate), text('INTERVAL 7 DAY'))

        already_participation = (
            db.query(ChallengeParticipant)
            .filter(
                ChallengeParticipant.userId == user_id,
                ChallengeParticipant.challenge.has(
                    and_(
                        Challenge.createdDate <= datetime.now(),
                        end_date > today_date,  
                    )
                )
            )
            .first()
        )
        if already_participation:
            raise HTTPException(status_code=400, detail="이미 참여 중인 챌린지가 있어 새로운 챌린지를 생성할 수 없습니다.")

        new_challenge = Challenge(
            name=challenge_data.name,
            publicityType=challenge_data.publicityType,
            password=challenge_data.password if not challenge_data.publicityType else None,
            challengeType=challenge_data.challengeType,
            goalCount=challenge_data.goalCount,
            createdDate=datetime.now()
        )
        db.add(new_challenge)
        db.flush()

        host = ChallengeParticipant(
            challengeId=new_challenge.challengeId, userId=user_id, isHost=True
        )
        db.add(host)
        db.commit()

        return new_challenge.challengeId 

    @staticmethod
    def join_challenge(db: Session, user_id: int, challenge_data: ChallengeJoin):

        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = func.date_add(func.date(Challenge.createdDate), text('INTERVAL 7 DAY'))

        already_joined = db.query(ChallengeParticipant).filter_by(
            userId=user_id,
            challengeId=challenge_data.challengeId
        ).first()
        if already_joined:
            raise HTTPException(status_code=400, detail="이미 이 챌린지에 참여했습니다.")

        in_other_challenge = (
            db.query(ChallengeParticipant)
            .join(Challenge)
            .filter(
                ChallengeParticipant.userId == user_id,
                Challenge.challengeId != challenge_data.challengeId,
                end_date > today_date,  
            )
            .first()
        )
        if in_other_challenge:
            raise HTTPException(status_code=400, detail="이미 다른 챌린지에 참여 중입니다.")

        challenge = ChallengeValidateService.validate_challenge(db, challenge_data.challengeId)

        if not challenge.publicityType and challenge.password != challenge_data.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

        participants_count = db.query(ChallengeParticipant).filter_by(
            challengeId=challenge.challengeId
        ).count()
        if participants_count >= 5:
            raise HTTPException(status_code=400, detail="최대 인원을 초과했습니다.")

        participant = ChallengeParticipant(
            challengeId=challenge.challengeId,
            userId=user_id,
            isHost=False
        )
        db.add(participant)
        db.commit()

        return challenge.challengeId