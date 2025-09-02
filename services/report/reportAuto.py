from schemas.reportGPT import ReportRequest
from services.report.data import get_gpt_data, format_report_data
from services.report.reportGPT import generate_report
from services.report.reportRepo import ReportService
from services.ml.type import classify_type
from services.ml.budget import training_and_prediction
from datetime import datetime, timedelta
from models.record import Record
from db.session import get_db

import logging
logger = logging.getLogger(__name__)

async def scheduled_report(userId: int, request: ReportRequest):
    db = db = next(get_db()) 
    try:
        gpt_data = await get_gpt_data(userId, request, db)

        if not gpt_data or gpt_data['total_spend'] <= 0 or sum(gpt_data['emotion_count'].values()) == 0:
            logger.warning("데이터 부족. 리포트 생략")

        if request.period == "monthly":
            data_str = format_report_data(
                gpt_data['total_spend'],
                gpt_data['emotion_count'],
                gpt_data['spend_to_emotion'],
                gpt_data['most_emotion'],
                gpt_data.get('category_ranking')
            )
            consumption_type = classify_type(
                db=db,
                userId=userId,
                year=request.reportDate.year,
                month=request.reportDate.month
            )
            budget_prediction = None
        else:
            data_str = format_report_data(
                gpt_data['total_spend'],
                gpt_data['emotion_count'],
                gpt_data['spend_to_emotion'],
                gpt_data['most_emotion']
            )
            budget_prediction = training_and_prediction(db, userId)
            budget_prediction = int(budget_prediction[0]) if budget_prediction else None
            consumption_type = ""

        existing_report = ReportService.get_existing_report(db, userId, request.reportDate, request.period)
        if existing_report:
            logger.warning("이미 존재하는 리포트")
            return

        report = generate_report(
            period=request.period,
            data=data_str,
            tone=request.tone,
            spend_type=consumption_type or "",
            budget_prediction=budget_prediction
        )

        ReportService.save_report(
            db=db,
            userId=userId,
            reportDate=request.reportDate,
            reportType=request.period,
            reportText=report,
            spendType=consumption_type
        )

        logger.info("리포트 생성 완료")
    finally:
        db.close()

async def generate_monthly_report():
    db = next(get_db())
    try:
        today = datetime.today()
        user_ids = db.query(Record.userId).distinct().all()
        user_id_list = [user_id for (user_id,) in user_ids]
        request = ReportRequest(
            reportDate=(today.replace(day=1) - timedelta(days=1)).replace(day=1).date(),
            tone="차분하게",
            period="monthly"
        )

        for user_id in user_id_list:
            logger.info(f"월간 리포트 생성 중: userId={user_id}")
            await scheduled_report(user_id, request)
    finally:
        db.close()

async def generate_weekly_report():
    db = next(get_db())
    try:
        user_ids = db.query(Record.userId).distinct().all()
        user_id_list = [user_id for (user_id,) in user_ids]

        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday() + 7)
        request = ReportRequest(
            reportDate=start_of_week.date(),
            tone="차분하게",
            period="weekly"
        )

        for user_id in user_id_list:
            logger.info(f"주간 리포트 생성 중: userId={user_id}")
            await scheduled_report(user_id, request)
    finally:
        db.close()


