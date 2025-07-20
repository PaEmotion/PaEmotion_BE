# main.py

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers.user.user import router as user_router 
from routers.user.email import router as email_router
from routers.record import router as record_router
from routers.report.data import router as report_data_router
from routers.report.report import router as report_router
from routers.ml.report import router as budget_router
app = FastAPI()

app.include_router(user_router)
app.include_router(email_router)
app.include_router(record_router) 
app.include_router(report_data_router)
app.include_router(report_router)
app.include_router(budget_router)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
