from pydantic import BaseModel, field_validator
from pydantic import EmailStr
from schemas.validator import validate_password

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
        return validate_password(v)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password(v)
    
class PasswordReset(BaseModel):
    token: str
    new_password : str

    @field_validator('new_password')
    def validate_password(cls, v):
        return validate_password(v)
    
class NicknameUpdate(BaseModel):
    new_nickname: str