from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from schemas.reportRepo import reportSave, ReportRead
from services.report.reportRepo import ReportService
from db.session import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

# 리포트 단건 조회 라우터 (URL에서 리포트 아이디 받음)
@router.get("/{reportId}", response_model=ReportRead)
def reports_read(
    reportId: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        report = ReportService.reports_read(db=db, report_id=reportId)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

# 리포트 목록 조회 라우터 (유저 아이디, 기간 또는 날짜를 쿼리파라미터로 받음)
@router.get("", response_model=List[ReportRead])
def reports_readbylist(
    userId: Optional[int] = Query(None),
    reportDate: Optional[date] = Query(None),
    startDate: Optional[date] = Query(None),
    endDate: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    if reportDate and (startDate or endDate):
        raise HTTPException(status_code=400, detail="reportDate는 startDate/endDate와 함께 사용할 수 없습니다.")
    if not userId and not reportDate and not (startDate and endDate):
        raise HTTPException(status_code=400, detail="최소한 userId, reportDate 또는 startDate+endDate 중 하나는 입력해야 합니다.")
    if (startDate and not endDate) or (endDate and not startDate):
        raise HTTPException(status_code=400, detail="startDate와 endDate는 함께 입력해야 합니다.")

    return ReportService.reports_readbylist(
        db=db,
        user_id=userId,
        report_date=reportDate,
        start_date=startDate,
        end_date=endDate
    )