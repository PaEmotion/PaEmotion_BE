from auth.dependencies import redis_client, get_all_user_ids
from services.scheduler.fcm import send_fcm

def send_weekly_notification():
    for user_id in get_all_user_ids():

        key = f"user:{user_id}:weekly_notification_sent"

        if redis_client.get(key):
            print(f"User {user_id} 이번주 알림 이미 발송")
            continue
        
        token = redis_client.get(f"user:{user_id}:fcm")
        if not token:
            print(f"User {user_id} 토큰 없음, 알림 발송 불가")
            continue
        
        send_fcm(token, "이번주 레포트 알림", "이번주 레포트가 도착했어요!")
        redis_client.set(key, 1, ex=7*24*3600)

def send_monthly_notification():
    for user_id in get_all_user_ids():

        key = f"user:{user_id}:weekly_notification_sent"

        if redis_client.get(key):
            print(f"User {user_id} 이번달 알림 이미 발송")
            continue
        
        token = redis_client.get(f"user:{user_id}:fcm")
        if not token:
            print(f"User {user_id} 토큰 없음, 알림 발송 불가")
            continue
        
        send_fcm(token, "이번달 레포트 알림", "이번달 레포트가 도착했어요!")
        redis_client.set(key, 1, ex=7*24*3600)