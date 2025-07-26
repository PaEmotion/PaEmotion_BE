from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from typing import Optional

from db.session import get_db
from schemas.record import RecordsCreate, RecordsRead, RecordsEdit
from services import record as record_service

router = APIRouter(prefix="/records", tags=["records"])

# 소비내역 생성 라우터
@router.post("/create", response_model=RecordsRead)
def create_records(record: RecordsCreate, db: Session = Depends(get_db)):
    new_record = record_service.create_records(db, record)
    return new_record

# 소비내역 조회 라우터
@router.get("/{userId}", response_model=List[RecordsRead]) # 기간
def readbydate_records(
    userId: int = Path(...),
    startDate: Optional[date] = Query(None),
    endDate: Optional[date] = Query(None),
    db: Session = Depends(get_db) 
):
    if not startDate or not endDate:
        raise HTTPException(status_code=400, detail="startDate와 endDate를 모두 입력해야 합니다.")
    result = record_service.readbydate_records(db=db, user_id=userId,  start_date=startDate, end_date=endDate)

    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result

@router.get("/{userId}/{spendId}", response_model=RecordsRead) # 단건
def read_records(
    userId: int = Path(...),
    spendId: int = Path(...),
    db: Session = Depends(get_db)
):
    result = record_service.read_records(db=db, user_id=userId, spend_id=spendId)
    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result

# 소비내역 수정 라우터
@router.put("/edit/{spendId}", response_model=RecordsRead)
def edit_records(
    spendId: int = Path(...),
    edited_data: RecordsEdit = Body(...),
    db: Session = Depends(get_db)
):
    edited_record = record_service.edit_records(db, spendId, edited_data)
    if edited_record is None:
        raise HTTPException(status_code=404, detail="수정할 소비내역을 찾을 수 없습니다.")
    if edited_record == "not_change":
        raise HTTPException(status_code=400, detail="변경된 내용이 없습니다.")
    return edited_record

# 소비내역 삭제 라우터
@router.delete("/delete/{spendId}")
def delete_records(
    spendId: int = Path(...),
    db: Session = Depends(get_db)
):
    success = record_service.delete_records(db, spendId)
    if not success:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return {"message": "소비내역이 삭제되었습니다."}