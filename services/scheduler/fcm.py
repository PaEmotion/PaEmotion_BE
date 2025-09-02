import requests, firebase_admin
from firebase_admin import credentials, messaging
import os

FCM_JSON_PATH = os.getenv("FCM_JSON_PATH")

cred = credentials.Certificate(FCM_JSON_PATH)
firebase_app = firebase_admin.initialize_app(cred)

def send_fcm(token: str, title: str, body: str):

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token
    )

    response = messaging.send(message, app=firebase_app)
    return response