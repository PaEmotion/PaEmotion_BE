from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
from services.report.reportAuto import generate_monthly_report, generate_weekly_report 

scheduler = AsyncIOScheduler()

# 매월 1일 오전 9시에 월간 리포트 실행
scheduler.add_job(generate_monthly_report, 'cron', day=1, hour=9, minute=0)

# 매주 월요일 오전 9시에 주간 리포트 실행
scheduler.add_job(generate_weekly_report, 'cron', day_of_week='mon', hour=9, minute=0)

# 지금부터 5초 후에 한 번만 실행해보기 (테스트용)
run_time = datetime.now() + timedelta(seconds=5)
scheduler.add_job(generate_weekly_report, trigger='date', run_date=run_time)


def start_scheduler():
    scheduler.start()
    print("스케줄러 시작됨")
