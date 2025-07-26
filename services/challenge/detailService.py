from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from models.challenge import ChallengeParticipant
from schemas.challenge import ChallengeDetailRead, ChallengeMemberRead
from services.challenge.validateService import ChallengeValidateService
from services.challenge.calculateService import ChallengeCalculateService

class ChallengeDetailService:

    ## 챌린지 참여자 목록 조회 함수 ##
    @staticmethod
    def read_participants(db: Session, challenge_id: int) -> List[ChallengeParticipant]:
        return db.query(ChallengeParticipant).filter_by(challengeId=challenge_id).all()
    
    
    ## 챌린지 상세 정보 조회 통합 함수 ##
    @staticmethod
    def read_challenge_detail(db: Session, challenge_id: int, user_id: int) -> ChallengeDetailRead:
        
        challenge = ChallengeValidateService.validate_challenge(db, challenge_id)  # 1. 챌린지 유효성 검사 및 조회
        participants = ChallengeDetailService.read_participants(db, challenge_id)  # 2. 챌린지 참여자 목록 조회
        participants_contribution = ChallengeCalculateService.participants_rate(db, challenge, participants)  # 3. 개인별 소비 횟수 및 기여도 계산
        team_progress = ChallengeCalculateService.team_rate(challenge, participants_contribution)  # 4. 팀 진행률 및 기니피그 먹이 개수 계산
        
        # 5. 최종 결과 반환
        return ChallengeDetailRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            endDate=(challenge.createdDate + timedelta(days=6)).date(),
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