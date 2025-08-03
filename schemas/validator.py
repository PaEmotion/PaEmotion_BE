import re

def validate_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError('비밀번호는 8자 이상으로 입력해 주세요.')
    if not re.search(r'[A-Za-z]', v):
        raise ValueError('영어가 최소 1개 포함되어야 합니다.')
    if not re.search(r'\d', v):
        raise ValueError('숫자가 최소 1개 포함되어야 합니다.')
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
        raise ValueError('특수문자가 최소 1개 포함되어야 합니다.')
    return v
