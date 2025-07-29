from models.user import User
from auth.email_token import create_email_token
from sqlalchemy.orm import Session
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from auth.dependencies import EMAIL_TOKEN_EXPIRE_MINUTES, redis_client, SMTP_USER, SMTP_PASSWORD

from dotenv import load_dotenv
load_dotenv()

class EmailService:

    # 2번 - 이메일 인증 요청을 눌렀을 때 인증 메일을 보낼 준비를 함
    @staticmethod
    async def send_verification_email(email:str, db:Session):
        try:
            existing_user = db.query(User).filter(User.email == email).first()
            if existing_user:
                raise ValueError("이미 존재하는 이메일입니다.")
            
            # 토큰 만들기 함수 (auth의)
            token = create_email_token(email)

            # Redis에 token 저장하기
            expire_seconds = EMAIL_TOKEN_EXPIRE_MINUTES * 60
            redis_client.set(token, email, ex=expire_seconds)

            subject = "이메일 인증을 완료해 주세요."
            verification_url = f"http://localhost:8000/verify-email?token={token}"

            content = f"""
                안녕하세요, PaEmotion 입니다.
                회원가입을 원하신다면 아래 링크를 클릭해 이메일 인증 완료해 주세요. 
                본인이 시도하신 회원가입이 아니라면, 링크를 누르지 마세요.

                {verification_url}

                감사합니다.
            """
            EmailService.send_email_smtp(email, subject, content)

            return token
        except Exception as e:
            print("🔥 이메일 인증 발송 중 오류:", str(e))
            raise
    
    # 3번 - SMTP로 실제 이메일 보내는 함수
    @staticmethod
    def send_email_smtp(to_email:str, subject:str, body: str):
        smtp_server = "smtp.naver.com"
        smtp_port = 587
        smtp_user = SMTP_USER
        smtp_password = SMTP_PASSWORD
        
        print("📧 Loaded SMTP_USER:", SMTP_USER)

        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body,"plain"))

        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)

            server.sendmail(smtp_user, to_email, msg.as_string())
            server.quit()

            print (f"이메일 전송 성공 : {to_email}")
        except Exception as e:
            print(f"이메일 전송 실패 : {str(e)}")
            raise e
            