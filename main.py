from db.session import SessionLocal
from db.base import Base

# 예시: raw SQL
def test_select():
    session = SessionLocal()
    try:
        result = session.execute("SELECT * FROM user")  # 테이블명 맞게 바꿔
        for row in result:
            print(row)
    finally:
        session.close()

test_select()
