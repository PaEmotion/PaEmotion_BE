from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeListRead, ChallengeRead, ChallengeDetailRead, ChallengeMemberRead
from services.challenge.validateService import ChallengeValidateService
from services.challenge.participantService import ChallegeParticipantService
from services.challenge.calculateService import ChallengeCalculateService

## 챌린지 조회 함수 (1, 2, 3) ##
class ChallengeReadService:
    
    ## 1. 챌린지 목록 조회 함수
    def read_challenges_list(db: Session) -> List[ChallengeListRead]:

        # 현재 날짜 조회
        current_date = datetime.now().date()

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
            if end_date.date() >= current_date:
                challenges_list.append(
                    ChallengeListRead(
                        challengeId=challenge.challengeId,
                        name=challenge.name,
                        publicityType=challenge.publicityType,
                        challengeType=challenge.challengeType,
                        endDate=end_date.date(),
                        participantCount=participants_count,
                    )
                )

        # 결과 반환 
        return challenges_list

    ## 2. 챌린지 단건 조회 함수
    @staticmethod
    def read_challenge(db: Session, challenge_id: int) -> ChallengeRead:

        # 현재 날짜 조회
        current_date = datetime.now().date()

        # 챌린지 유효성 검증 및 조회
        challenge = ChallengeValidateService.validate_challenge(db, challenge_id)

        # 종료된 챌린지면 예외 반환
        end_date = challenge.createdDate + timedelta(days=6) 
        if end_date.date() < current_date:
            raise HTTPException(status_code=400, detail="챌린지 기간이 종료되었습니다.")

        # 참여자 수 조회
        participants_count = (
            db.query(ChallengeParticipant)
            .filter(ChallengeParticipant.challengeId == challenge_id)
            .count()
        )

        # 결과 반환
        return ChallengeRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            endDate=end_date.date(),
            goalCount=challenge.goalCount,
            participantCount=participants_count,
        )
    
    ## 3. 챌린지 상세 정보 조회 통합 함수
    @staticmethod
    def read_challenge_detail(db: Session, challenge_id: int, user_id: int) -> ChallengeDetailRead:
        
        challenge = ChallengeValidateService.validate_challenge(db, challenge_id)  # 챌린지 유효성 검사 및 조회
        participants = ChallegeParticipantService.read_participants(db, challenge_id)  # 챌린지 참여자 목록 조회
        participants_contribution = ChallengeCalculateService.participants_rate(db, challenge, participants)  # 개인별 소비 횟수 및 기여도 계산
        team_progress = ChallengeCalculateService.team_rate(challenge, participants_contribution)  # 팀 진행률 및 기니피그 먹이 개수 계산
        
        # 최종 결과 반환
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
