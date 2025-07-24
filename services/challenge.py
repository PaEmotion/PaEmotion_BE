from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from fastapi import HTTPException

from models.challenge import Challenge, ChallengeParticipant
from models.record import Record
from models.user import User
from schemas.challenge import (ChallengeCreate, ChallengeJoin, ChallengeListRead,
    ChallengeRead, ChallengeDetailRead, ChallengeMemberRead)

class ChallengeService:

    ## 챌린지 생성 함수
    @staticmethod
    def create_challenge(db: Session, user_id: int, challenge_data: ChallengeCreate):

        # 1. 챌린지 종료일 계산
        created_date = datetime.utcnow().date()
        end_date = created_date + timedelta(days=7)

        # 2. 새로운 챌린지 생성
        new_challenge = Challenge(
            name=challenge_data.name,
            publicityType=challenge_data.publicityType,
            password=challenge_data.password if not challenge_data.publicityType else None,
            challengeType=challenge_data.challengeType,
            goalCount=challenge_data.goalCount,
            createdDate=created_date
        )
        db.add(new_challenge)
        db.flush() 

        # 3. 챌린지 생성자를 방장으로 등록
        host_participant = ChallengeParticipant(
            challengeId=new_challenge.challengeId,
            userId=user_id,
            isHost=True
        )
        db.add(host_participant)

        # 4. DB 반영
        db.commit()

    ## 챌린지 참여 함수
    @staticmethod
    def join_challenge(db: Session, user_id: int, challenge_data: ChallengeJoin):
        
        # 1. 현재 날짜 조회
        current_date = datetime.utcnow().date()

        # 2. 이미 참여한 챌린지가 있는지 확인
        exists = db.query(ChallengeParticipant).join(Challenge).filter(
            ChallengeParticipant.userId == user_id,
            (Challenge.createdDate + timedelta(days=7)) > current_date
        ).first()
        if exists:
            raise HTTPException(status_code=400, detail="이미 챌린지에 참여 중입니다.")

        # 3. 챌린지 조회 및 검증
        challenge = db.query(Challenge).filter_by(challengeId=challenge_data.challengeId).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        if not challenge.publicityType and challenge.password != challenge_data.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        if db.query(ChallengeParticipant).filter_by(challengeId=challenge_data.challengeId).count() >= 5:
            raise HTTPException(status_code=400, detail="최대 인원을 초과했습니다.")

        # 4. 참여자로 등록
        participant = ChallengeParticipant(
            challengeId=challenge_data.challengeId,
            userId=user_id,
            isHost=False
        )
        db.add(participant)
        db.commit()

    ## 챌린지 리스트 조회 함수
    @staticmethod
    def read_challenges_list(db: Session):
  
        # 1. 현재 날짜 조회
        current_date = datetime.utcnow().date()

        # 2. 모든 챌린지 정보 + 해당 챌린지 참여자 수 조회 
        results = db.query(
            Challenge,
            func.count(ChallengeParticipant.userId).label("participant_count")
        ).outerjoin(
            ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId
        ).group_by(
            Challenge.challengeId
        ).all()

        # 3. 기간이 유효한 챌린지만 필터링
        challenges_list = []
        for challenge, participant_count in results:
            end_date = challenge.createdDate + timedelta(days=7)
            if end_date > current_date:
                challenges_list.append({
                    "challengeId": challenge.challengeId,
                    "name": challenge.name,
                    "publicityType": challenge.publicityType,
                    "challengeType": challenge.challengeType,
                    "endDate": end_date,
                    "participantCount": participant_count
                })

        # 4. 결과 반환
        return challenges_list

    ## 챌린지 단건 조회 함수
    @staticmethod
    def read_challenge(db: Session, challenge_id: int):
  
        # 1. 현재 날짜 조회
        current_date = datetime.utcnow().date()

        # 2. 챌린지 조회 및 검증
        challenge = db.query(Challenge).filter(Challenge.challengeId == challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        # 3. 종료된 챌린지면 예외 반환
        end_date = challenge.createdDate + timedelta(days=7)
        if end_date <= current_date:
            raise HTTPException(status_code=400, detail="챌린지 기간이 종료되었습니다.")

        # 4. 참여자 수 조회
        participant_count = db.query(ChallengeParticipant).filter(
            ChallengeParticipant.challengeId == challenge_id
        ).count()

        # 5. 결과 반환
        return {
            "challengeId": challenge.challengeId,
            "name": challenge.name,
            "publicityType": challenge.publicityType,
            "challengeType": challenge.challengeType,
            "endDate": end_date,
            "participantCount": participant_count
        }

    ## 챌린지 검색 함수
    @staticmethod
    def search_challenge(db: Session, query: str) -> list[ChallengeListRead]:
        
        # 1. 현재 날짜 조회
        current_date = datetime.utcnow().date()
        
        # 2. 챌린지 이름에 검색어 포함된 챌린지 모두 조회
        all_challenges = db.query(Challenge).filter(
            Challenge.name.ilike(f"%{query}%")
        ).all()

        # 3. 기간이 유효한 챌린지만 필터링
        challenges_list = []
        for challenge in all_challenges:
            end_date = challenge.createdDate + timedelta(days=7)
            if end_date > current_date:
                challenges_list.append(challenge)

        # 4. 결과 반환
        return challenges_list

    ## 챌린지 상세 정보 조회 함수
    @staticmethod
    def read_challenge_detail(db: Session, challenge_id: int, user_id: int) -> ChallengeDetailRead:
        
        # 1. 챌린지 조회 및 검증
        challenge = db.query(Challenge).filter_by(challengeId=challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        # 2. 종료일 계산
        end_date = challenge.createdDate + timedelta(days=7)
        
        # 3. 유저별 정보가 입력될 리스트 생성
        members = db.query(ChallengeParticipant).filter_by(challengeId=challenge_id).all()
        member_info = []

        # 4. 기니 먹이 개수 최대 최소 계산
        guinea_feed_count = len(members) * challenge.goalCount
        
        # 5. 팀 누적 소비 횟수 초기화
        team_total_spend = 0

        # 6. 개인별 소비 횟수 집계
        for member in members:
            spend_count = db.query(Record).filter(
                Record.userId == member.userId,
                Record.spendDate >= challenge.createdDate,
                Record.spendDate <= end_date
            ).count()
            
            # 7. 팀 누적 소비 횟수에 반영
            team_total_spend += spend_count

            # 8. 개인별 기여도 계산
            if challenge.challengeType:  # 긍정
                contribution = min(spend_count / challenge.goalCount, 1.0)
            else:  # 부정
                contribution = max((challenge.goalCount - spend_count) / challenge.goalCount, 0.0)

            # 9. 유저별 정보(방장 여부와 기여도) 리스트에 입력
            member_info.append(ChallengeMemberRead(
                userId=member.userId,
                isHost=member.isHost,
                contribution=round(contribution * 100, 1)
            ))

        # 10. 팀 진행률 계산
        if challenge.challengeType: # 긍정
            progress = team_total_spend / guinea_feed_count
        else: # 부정
            progress = max((guinea_feed_count - team_total_spend) / guinea_feed_count, 0.0)

        # 11. 최종 결과 반환
        return ChallengeDetailRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            challengeType=challenge.challengeType,
            createdDate=challenge.createdDate,
            endDate=end_date,
            members=member_info,
            progress=round(progress * 100, 1)
        )