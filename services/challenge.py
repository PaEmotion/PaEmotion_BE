from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime, timedelta
from fastapi import HTTPException
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from models.record import Record
from models.user import User
from schemas.challenge import (ChallengeCreate, ChallengeJoin, ChallengeListRead,
    ChallengeRead, ChallengeDetailRead, ChallengeMemberRead,)

class ChallengeService:

    ## 챌린지 생성 함수
    @staticmethod
    def create_challenge(db: Session, user_id: int, challenge_data: ChallengeCreate):

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 현재 참여 중인 챌린지가 있는지 확인
        already_participation = (
            db.query(ChallengeParticipant)
            .join(Challenge, Challenge.challengeId == ChallengeParticipant.challengeId)
            .filter(
                ChallengeParticipant.userId == user_id,
                Challenge.createdDate <= current_date,
                Challenge.createdDate + timedelta(days=7) > current_date 
            )
            .first()
        )

        if already_participation:
            raise HTTPException(status_code=400, detail="이미 참여 중인 챌린지가 있어 새로운 챌린지를 생성할 수 없습니다.")
        
        # 3. 챌린지 종료일 계산
        end_date = current_date + timedelta(days=7)

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
        host_participant = ChallengeParticipant(
            challengeId=new_challenge.challengeId, userId=user_id, isHost=True
        )
        db.add(host_participant)

        # 6. DB 반영
        db.commit()

    ## 챌린지 참여 함수
    @staticmethod
    def join_challenge(db: Session, user_id: int, challenge_data: ChallengeJoin):

        # 1. 현재 날짜 조회
        current_date = datetime.now()

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
                (Challenge.createdDate + timedelta(days=7)) > current_date,
            )
            .first()
        )

        if in_other_challenge:
            raise HTTPException(status_code=400, detail="이미 다른 챌린지에 참여 중입니다.")

        # 4. 챌린지 조회 및 검증
        challenge = db.query(Challenge).filter_by(challengeId=challenge_data.challengeId).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        if not challenge.publicityType and challenge.password != challenge_data.password:
            raise HTTPException(status_code=403, detail="비밀번호가 일치하지 않습니다.")
        if (
            db.query(ChallengeParticipant)
            .filter_by(challengeId=challenge_data.challengeId)
            .count() >= 5
        ):
            raise HTTPException(status_code=400, detail="최대 인원을 초과했습니다.")

        # 5. 참여자로 등록
        participant = ChallengeParticipant(
            challengeId=challenge_data.challengeId, userId=user_id, isHost=False
        )
        db.add(participant)
        db.commit()

    ## 챌린지 리스트 조회 함수
    @staticmethod
    def read_challenges_list(db: Session) -> List[ChallengeListRead]:

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 모든 챌린지 정보 + 해당 챌린지 참여자 수 조회
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .group_by(Challenge.challengeId)
            .all()
        )

        # 3. 기간이 유효한 챌린지만 필터링하여 리스트에 추가
        challenges_list = []
        for challenge, participant_count in results:
            end_date = challenge.createdDate + timedelta(days=7)
            if end_date > current_date:
                challenges_list.append(
                    ChallengeListRead(
                        challengeId=challenge.challengeId,
                        name=challenge.name,
                        publicityType=challenge.publicityType,
                        challengeType=challenge.challengeType,
                        createdDate=challenge.createdDate,
                        participantCount=participant_count,
                    )
                )

        # 4. 결과 반환 
        return challenges_list

    ## 챌린지 단건 조회 함수
    @staticmethod
    def read_challenge(db: Session, challenge_id: int) -> ChallengeRead:

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 챌린지 조회 및 검증
        challenge = db.query(Challenge).filter(Challenge.challengeId == challenge_id).first()
        if not challenge:
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")

        # 3. 종료된 챌린지면 예외 반환
        end_date = challenge.createdDate + timedelta(days=7)
        if end_date <= current_date:
            raise HTTPException(status_code=400, detail="챌린지 기간이 종료되었습니다.")

        # 4. 참여자 수 조회
        participant_count = (
            db.query(ChallengeParticipant).filter(ChallengeParticipant.challengeId == challenge_id).count()
        )

        # 5. 결과 반환
        return ChallengeRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            createdDate=challenge.createdDate,
            goalCount=challenge.goalCount,
            participantCount=participant_count,
        )

    ## 챌린지 검색 함수
    @staticmethod
    def search_challenge(db: Session, query: str) -> List[ChallengeListRead]:

        # 1. 현재 날짜 조회
        current_date = datetime.now()

        # 2. 검색어 포함 + 챌린지 기간 유효한 챌린지와 참여자 수 조회 쿼리 실행
        results = (
            db.query(
                Challenge,
                func.count(ChallengeParticipant.userId).label("participant_count"),
            )
            .outerjoin(ChallengeParticipant, Challenge.challengeId == ChallengeParticipant.challengeId)
            .filter(
                Challenge.name.ilike(f"%{query}%"),
                (Challenge.createdDate + timedelta(days=7)) > current_date,
            )
            .group_by(Challenge.challengeId)
            .all()
        )

        # 3. 검색 결과 시 유효한 챌린지를 리스트에 추가
        challenges_list = []
        for challenge, participant_count in results:
            challenges_list.append(
                ChallengeListRead(
                    challengeId=challenge.challengeId,
                    name=challenge.name,
                    challengeType=challenge.challengeType,
                    publicityType=challenge.publicityType,
                    createdDate=challenge.createdDate,
                    participantCount=participant_count,
                )
            )

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

        # 3. 참여자 조회
        members = db.query(ChallengeParticipant).filter_by(challengeId=challenge_id).all()
        member_info = []

        # 4. 목표 기니 먹이 개수 계산
        guinea_feed_goal = len(members) * challenge.goalCount

        # 5. 팀 누적 소비 횟수 초기화
        team_total_spend = 0

        # 6. 감정 ID 긍정/부정 분류 
        positive_emotion_ids = [1, 2, 3]  
        negative_emotion_ids = [4, 5, 6, 7, 8, 9, 10, 11, 12]  

        # 7. 개인별 소비 횟수 기간, 감정 별로 필터링하여 집계
        for member in members:
            if challenge.challengeType:  # 긍정
                emotion_filter = Record.emotionCategoryId.in_(positive_emotion_ids)
            else:  # 부정
                emotion_filter = Record.emotionCategoryId.in_(negative_emotion_ids)

            spend_count = (
                db.query(Record)
                .filter(
                    Record.userId == member.userId,
                    Record.spendDate >= challenge.createdDate,
                    Record.spendDate <= end_date,
                    emotion_filter
                )
                .count()
            )

            # 8. 팀 누적 소비 개수에 반영 (초과분은 반영 X)
            team_total_spend += min(spend_count, challenge.goalCount)

            # 9. 개인 별 기여도 계산
            if challenge.challengeType:  # 긍정
                contribution = min(spend_count / challenge.goalCount, 1.0)
            else:  # 부정
                contribution = max((challenge.goalCount - spend_count) / challenge.goalCount, 0.0)

            # 10. 멤버 별 정보(방장 여부, 기여도) 리스트에 저장
            member_info.append(
                ChallengeMemberRead(
                    userId=member.userId,
                    isHost=member.isHost,
                    contributionRate=round(contribution * 100, 1),
                )
            )

        # 11. 팀 전체 진행률 및 현재 기니피그 먹이 개수 계산
        if challenge.challengeType:  # 긍정
            progress = team_total_spend / guinea_feed_goal if guinea_feed_goal > 0 else 0.0
            guinea_feed_current = min(team_total_spend, guinea_feed_goal)  

        else:  # 부정
            progress = max((guinea_feed_goal - team_total_spend) / guinea_feed_goal, 0.0) if guinea_feed_goal > 0 else 0.0
            guinea_feed_current = max(guinea_feed_goal - team_total_spend, 0)

        # 12. 최종 응답 반환 
        return ChallengeDetailRead(
            challengeId=challenge.challengeId,
            name=challenge.name,
            publicityType=challenge.publicityType,
            challengeType=challenge.challengeType,
            createdDate=challenge.createdDate,
            goalCount=challenge.goalCount,
            guineaFeedCurrent=guinea_feed_current,
            teamProgressRate=round(progress * 100, 1),
            members=member_info
        )