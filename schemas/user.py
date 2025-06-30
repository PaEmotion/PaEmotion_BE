from pydantic import BaseModel, field_validator
from pydantic import EmailStr
import re

class UserCreate(BaseModel):
    name: str
    nickname: str
    password: str
    email: EmailStr

    @field_validator('name', 'nickname')
    @classmethod
    def validate_name_nickname(cls, v: str) -> str:
        if not (1 <= len(v) <= 7):
            raise ValueError('1자 이상 7자 이하로 입력해 주세요.')
        if ' ' in v:
            raise ValueError('띄어쓰기는 허용되지 않습니다.')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('비밀번호는 8자 이상으로 입력해 주세요.')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('영어가 최소 1개 포함되어야 합니다.')
        if not re.search(r'\d', v):
            raise ValueError('숫자가 최소 1개 포함되어야 합니다.')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('특수문자가 최소 1개 포함되어야 합니다.')
        return v

class UserLogin(BaseModel):
    email: str
    password: str