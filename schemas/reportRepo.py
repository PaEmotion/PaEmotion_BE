from pydantic import BaseModel
from datetime import date
from enum import Enum as PyEnum
from typing import Optional

class ReportTypeEnum(str, PyEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class reportSave(BaseModel):
    reportDate: date
    reportType: ReportTypeEnum
    reportText: str
    spendType: Optional[str] = ""

class ReportRead(reportSave):
    reportId: int
    userId: int

    class Config: from_attributes = True