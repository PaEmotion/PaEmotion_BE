# main.py

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers.user.user import router as user_router 
from routers.user.email import router as email_router
from routers.record import router as record_router

app = FastAPI()

app.include_router(user_router)
app.include_router(email_router)
app.include_router(record_router) 

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
