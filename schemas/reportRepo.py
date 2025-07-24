from pydantic import BaseModel
from datetime import date
from enum import Enum as PyEnum

class ReportTypeEnum(str, PyEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

# 리포트 저장 스키마
class reportSave(BaseModel):
    reportDate: date
    reportType: ReportTypeEnum
    reportText: str
    spendType: str

# 리포트 조회 스키마
class ReportRead(reportSave):
    reportId: int
    userId: int

    class Config: from_attributes = True