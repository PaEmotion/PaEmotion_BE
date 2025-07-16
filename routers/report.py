from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from schemas.report import ReportCreate, ReportRead
from services.report import ReportService
from db.session import get_db

router = APIRouter(prefix="/report", tags=["report"])

# 리포트 저장 API
@router.post("/create/{userId}", response_model=ReportRead, status_code=201)
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
@router.get("/read/{reportId}", response_model=ReportRead)
def report_read(
    reportId: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        report = ReportService.report_read(db=db, report_id=reportId)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 리포트 목록 조회 API (유저 아이디, 기간 또는 날짜를 쿼리파라미터로 받음)
@router.get("/readbylist", response_model=List[ReportRead])
def report_readbylist(
    userId: int = Query(...),
    startDate: Optional[date] = Query(None),
    endDate: Optional[date] = Query(None),
    reportDate: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    if reportDate and (startDate or endDate):
        raise HTTPException(status_code=400, detail="reportDate와 startDate/endDate를 동시에 사용할 수 없습니다.")
    if not reportDate and not (startDate and endDate):
        raise HTTPException(status_code=400, detail="reportDate 또는 startDate + endDate를 입력해주세요.")

    return ReportService.report_readbylist(
        db=db,
        user_id=userId,
        start_date=startDate,
        end_date=endDate,
        report_date=reportDate
    )