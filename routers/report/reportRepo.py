from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from utils.response import response_success
from schemas.reportRepo import ReportRead
from services.report.reportRepo import ReportService
from db.session import get_db

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/{reportId}", response_model=ReportRead)
def read_report(
    reportId: int = Path(...),
    db: Session = Depends(get_db)
):
    try:
        report = ReportService.read_report(db=db, report_id=reportId)
        return response_success(data=report, message="리포트 단건 조회 성공")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

from fastapi.encoders import jsonable_encoder

@router.get("", response_model=List[ReportRead])
def readbylist_reports(
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

    result = ReportService.readbylist_reports(
        db=db,
        user_id=userId,
        report_date=reportDate,
        start_date=startDate,
        end_date=endDate
    )

    # ORM 객체를 직렬화 가능한 형태로 변환
    result_serialized = jsonable_encoder(result)

    return response_success(data=result_serialized, message="리포트 조회 성공")
