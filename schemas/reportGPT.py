from pydantic import BaseModel, model_validator, ValidationError
from typing import Literal, Optional
from datetime import date

class ReportRequest(BaseModel):
    period: Literal["weekly", "monthly"]
    tone: str
    reportDate:date