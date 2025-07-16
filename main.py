# main.py

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers.user.user import router as user_router 
from routers.user.email import router as email_router
from routers.record.record import router as record_router
from routers.record.ml_record import router as ml_record_router
from routers.report import router as report_router
app = FastAPI()

app.include_router(user_router)
app.include_router(email_router)
app.include_router(record_router) 
app.include_router(ml_record_router)
app.include_router(report_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
