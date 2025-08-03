from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class RecordsCreate(BaseModel):
    userId: int
    emotionCategoryId: int
    spendCategoryId: int
    spendItem: str
    spendCost: int
    spendDate: datetime

class RecordsRead(RecordsCreate):
    spendId: int 
    class Config: from_attributes = True

class RecordsEdit(BaseModel):
    emotionCategoryId: Optional[int] = None
    spendCategoryId: Optional[int] = None
    spendItem: Optional[str] = None
    spendCost: Optional[int] = None
    spendDate: Optional[datetime] = None
