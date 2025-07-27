from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from fastapi import HTTPException

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeCreate, ChallengeJoin
from services.challenge.validateService import ChallengeValidateService

class ChallengeBasicService:
    
    ## 챌린지 생성 함수 ##
    @staticmethod
    def create_challenge(db: Session, user_id: int, challenge_data: ChallengeCreate):

        # 1. 현재 날짜 조회
        current_date = datetime.now().date()

        # 2. 현재 참여 중인 챌린지가 있는지 확인
        already_participation = (
            db.query(ChallengeParticipant)
            .filter(
                ChallengeParticipant.userId == user_id,
                ChallengeParticipant.challenge.has(
                and_(
                    Challenge.createdDate <= current_date,
                    Challenge.createdDate + timedelta(days=6) >= current_date
                )
            )
        )
        .first()
        )
        if already_participation:
            raise HTTPException(status_code=400, detail="이미 참여 중인 챌린지가 있어 새로운 챌린지를 생성할 수 없습니다.")
        
        # 3. 챌린지 종료일 계산
        end_date = (current_date + timedelta(days=6))

        # 4. 새로운 챌린지 생성
        new_challenge = Challenge(
            name=challenge_data.name,
            publicityType=challenge_data.publicityType,
            password=challenge_data.password if not challenge_data.publicityType else None,
            challengeType=challenge_data.challengeType,
            goalCount=challenge_data.goalCount,
            createdDate=current_date
        )
        db.add(new_challenge)
        db.flush()

        # 5. 방장으로 등록
        host = ChallengeParticipant(
            challengeId=new_challenge.challengeId, userId=user_id, isHost=True
        )
        db.add(host)

        # 6. DB 반영
        db.commit()

    ## 챌린지 참여 함수 ##
    @staticmethod
    def join_challenge(db: Session, user_id: int, challenge_data: ChallengeJoin):

        # 1. 현재 날짜 조회
        current_date = datetime.now().date()

        # 2. 동일 챌린지에 이미 참여했는지 확인
        already_joined = db.query(ChallengeParticipant).filter_by(
            userId=user_id,
            challengeId=challenge_data.challengeId
        ).first()
        if already_joined:
            raise HTTPException(status_code=400, detail="이미 이 챌린지에 참여했습니다.")

        # 3. 다른 챌린지에 참여중인지 확인
        in_other_challenge = (
            db.query(ChallengeParticipant)
            .join(Challenge)
            .filter(
                ChallengeParticipant.userId == user_id,
                Challenge.challengeId != challenge_data.challengeId,
                (Challenge.createdDate + timedelta(days=6)) >= current_date,
            )
            .first()
        )
        if in_other_challenge:
            raise HTTPException(status_code=400, detail="이미 다른 챌린지에 참여 중입니다.")

        # 4. 챌린지 유효성 검증 및 조회
        challenge = ChallengeValidateService.validate_challenge(db, challenge_data.challengeId)

        # 5. 비공개 챌린지일 경우 비밀번호 검증
        if not challenge.publicityType and challenge.password != challenge_data.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")

        # 6. 최대 인원 초과 여부 확인
        participants_count = db.query(ChallengeParticipant).filter_by(
            challengeId=challenge.challengeId
        ).count()
        if participants_count >= 5:
            raise HTTPException(status_code=400, detail="최대 인원을 초과했습니다.")

        # 7. 참여자로 등록
        participant = ChallengeParticipant(
            challengeId=challenge.challengeId,
            userId=user_id,
            isHost=False
        )
        db.add(participant)
        db.commit()