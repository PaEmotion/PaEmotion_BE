# main.py


from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from routers.user.user import router as user_router 
from routers.user.email import router as email_router
from routers.record.record import router as record_router
from routers.report.reportRepo import router as report_router
from routers.ml.budget import router as ml_budget_router
from routers.ml.type import router as type_router
from routers.report.reportGPT import router as reportGPT_router
from routers.budget.budget import router as budget_router
from routers.challenge.challenge import router as challenge_router
from schedulers.fcm import router as fcm_router
from utils.exception import custom_http_exception
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.scheduler.notification import send_weekly_notification, send_monthly_notification
from services.report.reportAuto import generate_monthly_report, generate_weekly_report 
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  
        ]
    )

setup_logging() 


scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(generate_monthly_report, 'cron', day=1, hour=9, minute=0)
    scheduler.add_job(generate_weekly_report, 'cron', day_of_week='mon', hour=9, minute=0)
    scheduler.add_job(send_weekly_notification, 'cron', day_of_week='mon', hour=9, minute=0)
    scheduler.add_job(send_monthly_notification, 'cron', day=1, hour=9, minute=0)


    scheduler.start()
    print("스케줄러 시작됨")
    yield

    scheduler.shutdown()
    print("스케줄러 종료됨")

app = FastAPI(lifespan=lifespan)


app.include_router(user_router)
app.include_router(email_router)
app.include_router(record_router) 
app.include_router(report_router)
app.include_router(ml_budget_router)
app.include_router(type_router)
app.include_router(reportGPT_router)
app.include_router(budget_router)
app.include_router(challenge_router)
app.include_router(fcm_router)
app.add_exception_handler(HTTPException, custom_http_exception)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
