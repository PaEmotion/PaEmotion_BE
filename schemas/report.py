from pydantic import BaseModel
from datetime import date
from enum import Enum as PyEnum

class ReportTypeEnum(str, PyEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

# 리포트 저장 스키마
class ReportCreate(BaseModel):
    reportDate: date
    reportType: ReportTypeEnum
    reportText: str

# 리포트 조회 스키마
class ReportRead(ReportCreate):
    reportId: int
    userId: int

    class Config:
        orm_mode = True
