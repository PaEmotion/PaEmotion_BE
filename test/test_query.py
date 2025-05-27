# test_query.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# DB 접속 URL 예시 (본인 환경에 맞게 수정)
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/paemotiondb"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True 하면 쿼리 로그 확인 가능
Session = sessionmaker(bind=engine)

def test_connection():
    session = Session()
    try:
        # 아주 간단하게 user 테이블에서 5개만 뽑아보기
        result = session.execute(text("SELECT * FROM user LIMIT 5"))
        for row in result:
            print(row)
        print("연결 성공 및 쿼리 실행 완료!")
    except Exception as e:
        print("오류 발생:", e)
    finally:
        session.close()

if __name__ == "__main__":
    test_connection()
