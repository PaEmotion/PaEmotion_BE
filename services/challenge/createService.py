from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from fastapi import HTTPException

from models.challenge import Challenge, ChallengeParticipant
from schemas.challenge import ChallengeCreate

## 챌린지 생성 함수 ##
class ChallengeCreateService:
    
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
        end_date = (current_date + timedelta(days=6)).date()

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