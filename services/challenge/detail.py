from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
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
        participants = ChallengeDetailService.read_participants(db, challenge_id)  
        participants_contribution = ChallengeCalculateService.participants_rate(db, challenge, participants) 
        team_progress = ChallengeCalculateService.team_rate(challenge, participants_contribution)  
        
        return ChallengeDetailRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            endDate=(challenge.createdDate + timedelta(days=6)),
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