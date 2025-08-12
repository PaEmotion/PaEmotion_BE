from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from services.report.reportAuto import generate_monthly_report, generate_weekly_report 
import logging
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

# 매월 1일 오전 9시에 월간 리포트 실행
scheduler.add_job(generate_monthly_report, 'cron', day=1, hour=9, minute=0)

# 매주 월요일 오전 9시에 주간 리포트 실행
scheduler.add_job(generate_weekly_report, 'cron', day_of_week='mon', hour=9, minute=0)


def start_scheduler():
    scheduler.start()
    logger.info("스케줄러 시작됨")
