from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from schemas.report import ReportCreate, ReportRead
from services.report import ReportService
from db.session import get_db

router = APIRouter()

# 리포트 저장 API
@router.post("/report/create/{userId}", response_model=ReportRead, status_code=201)
def report_create(
    userId: int = Path(...),
    report_data: ReportCreate = Body(...),
    db: Session = Depends(get_db)
):
    try:
        report = ReportService.report_create(
            db=db,
            user_id=userId,
            report_date=report_data.reportDate,
            report_type=report_data.reportType,
            report_text=report_data.reportText
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# 리포트 단건 조회 API (URL에서 리포트 아이디 받음)
@router.get("/report/read/{reportId}", response_model=ReportRead)
def report_read(
    reportId: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        report = ReportService.report_read(db=db, report_id=reportId)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# 리포트 목록 조회 API (유저아이디, 기간을 쿼리파라미터로 받음)
@router.get("/report/readbylist", response_model=List[ReportRead])
def report_readbylist(
    userId: Optional[int] = Query(None, description="유저 ID"),
    startDate: Optional[date] = Query(None, description="조회 시작일"),
    endDate: Optional[date] = Query(None, description="조회 종료일"),
    db: Session = Depends(get_db)
):
    return ReportService.report_readbylist(
        db=db,
        user_id=userId,
        start_date=startDate,
        end_date=endDate
    )
