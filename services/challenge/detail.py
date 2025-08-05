from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from fastapi import HTTPException

from models.challenge import ChallengeParticipant
from schemas.challenge import ChallengeDetailRead, ChallengeMemberRead
from services.challenge.validate import ChallengeValidateService
from services.challenge.calculate import ChallengeCalculateService

class ChallengeDetailService:

    @staticmethod
    def read_participants(db: Session, challenge_id: int) -> List[ChallengeParticipant]:
        return db.query(ChallengeParticipant).filter_by(challengeId=challenge_id).all()

    @staticmethod
    def read_challenge_detail(db: Session, challenge_id: int, user_id: int) -> ChallengeDetailRead:

        challenge = ChallengeValidateService.validate_challenge(db, challenge_id) 

        end_date = challenge.createdDate.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=7)
        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if end_date <= today_date:
            raise HTTPException(status_code=404, detail="챌린지 기간이 종료되었거나 존재하지 않습니다.")

        participants = ChallengeDetailService.read_participants(db, challenge_id)
        participants_contribution = ChallengeCalculateService.participants_rate(db, challenge, participants)
        team_progress = ChallengeCalculateService.team_rate(challenge, participants_contribution)

        return ChallengeDetailRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            endDate=end_date,
            goalCount=challenge.goalCount,
            guineaFeedCurrent=team_progress.guineaFeedCount,
            teamProgressRate=team_progress.teamProgressRate,
            participantsInfo=[
                ChallengeMemberRead(
                    userId=participant.userId,
                    isHost=participant.isHost,
                    contributionRate=participant.contributionRate
                ) for participant in participants_contribution
            ]
        )