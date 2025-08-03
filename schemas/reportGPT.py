from pydantic import BaseModel
from typing import Literal
from datetime import date

class ReportRequest(BaseModel):
    period: Literal["weekly", "monthly"]
    tone: str
    reportDate:date