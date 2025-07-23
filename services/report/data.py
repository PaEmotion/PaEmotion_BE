from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.record import Record
from models.category import EmotionCategory, SpendCategory
from schemas.reportGPT import ReportRequest
from datetime import timedelta
from collections import defaultdict

async def get_gpt_data(userId: int, request: ReportRequest, db: Session):
    if not request.reportDate:
        raise HTTPException(status_code=400, detail="기준 날짜(reportDate)를 반드시 입력해야 합니다.")

    start_date = request.reportDate

    if request.period == "weekly":
        end_date = start_date + timedelta(days=6)
    elif request.period == "monthly":
        # 이번 달 마지막 날 계산
        if start_date.month == 12:
            next_month = start_date.replace(year=start_date.year + 1, month=1, day=1)
        else:
            next_month = start_date.replace(month=start_date.month + 1, day=1)
        end_date = next_month - timedelta(days=1)
    else:
        raise HTTPException(status_code=400, detail="유효하지 않은 기간입니다.")

    records = (
        db.query(Record)
        .filter(
            Record.userId == userId,
            Record.spendDate >= start_date,
            Record.spendDate <= end_date
        )
        .all()
    )

    # 감정,소비 Id -> 감정,소비 이름 매핑
    emotion_category = db.query(EmotionCategory).all()
    emotion_to_name = {e.emotionCategoryId: e.emotionCategoryName for e in emotion_category}
    spend_category = db.query(SpendCategory).all()
    spend_to_name = {s.spendCategoryId: s.spendCategoryName for s in spend_category}

    emotion_count = defaultdict(int) # 느낀 감정의 횟수
    spend_to_emotion = defaultdict(int) # 감정 카테고리에 따른 소비 횟수
    spend_count = defaultdict(int) # 소비한 소비 카테고리의 횟수
    spend_to_spend = defaultdict(int) # 소비 카테고리에 따른 소비 횟수
    total_spend = 0

    for record in records:
        emotion = emotion_to_name.get(record.emotionCategoryId)
        category = spend_to_name.get(record.spendCategoryId)
        if emotion:
            emotion_count[emotion] += 1
            spend_to_emotion[emotion] += record.spendCost
        
        if category:
            spend_count[category] += 1
            spend_to_spend[category] += record.spendCost    
        
        total_spend += record.spendCost

    most_emotion = max(emotion_count.items(), key=lambda x:x[1])[0] if emotion_count else None

    spend_ranking = sorted(
        spend_count.items(), key=lambda x: spend_to_spend[x[0]], reverse=True
    )

    category_ranking = [
        {"category": cat, "count": spend_count[cat], "amount": spend_to_spend[cat]}
        for cat, _ in spend_ranking
    ]

    return {
        "total_spend": total_spend,
        "emotion_count": dict(emotion_count),
        "spend_to_emotion": dict(spend_to_emotion),
        "most_emotion": most_emotion,
        "category_ranking": category_ranking
    }

def format_report_data(total_spend, emotion_count, spend_to_emotion, most_emotion,category_ranking=None):
    lines = []
    lines.append(f"총 소비 금액: {total_spend:,}원")
    lines.append(f"가장 많이 느낀 감정: {most_emotion}")
    lines.append("감정 별 소비 내역:")
    for emotion, count in emotion_count.items():
        amount = spend_to_emotion.get(emotion, 0)
        lines.append(f"* {emotion} -> {count}회, 소비 {amount:,}원")

    if category_ranking:
        lines.append("\n그 다음으로, 이번 달 소비 카테고리 랭킹을 정리해 드리겠습니다.")
        for i, cat in enumerate(category_ranking[:3], start=1):  # 상위 3개만 예시
            lines.append(f"* {i}위: {cat['category']} 소비, 총 {cat['count']}회, {cat['amount']:,}원")
    return "\n".join(lines)
