from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from models.challenge import Challenge, ChallengeParticipant
from models.record import Record
from schemas.challenge import ChallengeMemberContribution, ChallengeTeamProgress

## 개인, 팀 관련 집계 계산 함수들 (1, 2) ##
class ChallengeCalculateService:

     ## 1. 멤버 소비 횟수 및 기여도 계산 함수
    @staticmethod
    def participants_rate(db: Session, challenge: Challenge, participants: List[ChallengeParticipant]
    ) -> List[ChallengeMemberContribution]:

        # 챌린지 종료일 계산
        end_date = challenge.createdDate + timedelta(days=6)

        # 감정 ID 긍정/부정 구분 필터 설정
        positive_emotion_ids = [1, 2, 3]
        negative_emotion_ids = [4, 5, 6, 7, 8, 9, 10, 11, 12]
        emotion_filter = Record.emotionCategoryId.in_(
            positive_emotion_ids if challenge.challengeType else negative_emotion_ids
        )

        # 최종 결과 담을 리스트 설정
        result = []

        # 챌린지 기간 내 개인 별 소비 횟수 집계
        for participant in participants:
            spend_count = db.query(Record).filter(
                Record.userId == participant.userId,
                Record.spendDate >= challenge.createdDate,
                Record.spendDate <= end_date,
                emotion_filter
            ).count()

            # 개인 별 기여도 계산 (소비내역 초과분 무시)
            if challenge.challengeType:  
                contribution = min(spend_count / challenge.goalCount, 1.0)
            else:  
                contribution = max((challenge.goalCount - spend_count) / challenge.goalCount, 0.0)

            # 유저 정보와 계산 결과 리스트에 저장
            result.append(ChallengeMemberContribution(
                userId=participant.userId,
                isHost=participant.isHost,
                spendCount=spend_count,
                contributionRate=round(contribution * 100, 1)
            )   )

        # 결과 반환
        return result
    
    ## 2. 팀 진행률 및 기니피그 먹이 계산 함수
    @staticmethod
    def team_rate(challenge: Challenge, participants: List[ChallengeMemberContribution]
    ) -> ChallengeTeamProgress:

        # 목표 기니 먹이 개수 계산
        guinea_feed_goal = len(participants) * challenge.goalCount

        # 챌린지 기간 내 팀 소비 총합 집계 (초과분 무시)
        team_total_spend = sum(
            min(participant.spendCount, challenge.goalCount) for participant in participants
        )

        # 팀 진행률 및 현재 기니 먹이 개수 계산
        if challenge.challengeType: 
            progress = team_total_spend / guinea_feed_goal
            guinea_feed_current = min(team_total_spend, guinea_feed_goal)
        else: 
            progress = max((guinea_feed_goal - team_total_spend) / guinea_feed_goal, 0.0)
            guinea_feed_current = max(guinea_feed_goal - team_total_spend, 0)

        # 결과 반환
        return ChallengeTeamProgress(
            teamProgressRate=round(progress * 100, 1),
            guineaFeedCount=guinea_feed_current
    )