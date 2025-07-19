from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# 소비내역 생성 스키마
class RecordsCreate(BaseModel):
    userId: int
    emotionCategoryId: int
    spendCategoryId: int
    spendItem: str
    spendCost: int
    spendDate: datetime

# 소비내역 조회 스키마
class RecordsRead(RecordsCreate):
    spendId: int 
    class Config: from_attributes = True

# 소비내역 수정 스키마
class RecordsEdit(BaseModel):
    emotionCategoryId: Optional[int] = None
    spendCategoryId: Optional[int] = None
    spendItem: Optional[str] = None
    spendCost: Optional[int] = None
    spendDate: Optional[datetime] = None
