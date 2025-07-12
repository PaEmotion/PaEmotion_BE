from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 소비 내역 생성 스키마
class RecordsCreate(BaseModel):
    user_id: int = Field(..., alias="userId")
    emotion_category_id: int = Field(..., alias="emotionCategoryId")
    spend_category_id: int = Field(..., alias="spendCategoryId")
    spend_item: str = Field(..., alias="spendItem")
    spend_cost: int = Field(..., alias="spendCost")
    spend_date: datetime = Field(..., alias="spendDate")

    class Config:
        allow_population_by_field_name = True

# 소비 내역 조회 스키마
class RecordsRead(RecordsCreate):
    spend_id: int = Field(..., alias="spendId")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# 소비 내역 삭제 스키마
class RecordsDelete(BaseModel):
    emotion_category_id: Optional[int] = Field(None, alias="emotionCategoryId")
    spend_category_id: Optional[int] = Field(None, alias="spendCategoryId")
    spend_item: Optional[str] = Field(None, alias="spendItem")
    spend_cost: Optional[int] = Field(None, alias="spendCost")
    spend_date: Optional[datetime] = Field(None, alias="spendDate")

    class Config:
        allow_population_by_field_name = True