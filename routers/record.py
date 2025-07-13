from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from schemas.record import RecordsCreate, RecordsRead, RecordsEdit
from db.session import get_db
from services import record as record_service

router = APIRouter(prefix="/records", tags=["records"])

# 소비내역 생성 API
@router.post("/create", response_model=RecordsRead)
def records_create(record: RecordsCreate, db: Session = Depends(get_db)):
    new_record = record_service.records_create(db, record)
    return new_record

# 소비내역 조회 API
@router.get("/readbydate/{userId}", response_model=List[RecordsRead])  # 일건
def readbydate(
    userId: int = Path(...),
    spendDate: date = Query(...),
    db: Session = Depends(get_db)
):
    result = record_service.records_readbydate(db=db, user_id=userId, spend_date=spendDate)
    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result
@router.get("/readbyspendid/{userId}/{spendId}", response_model=RecordsRead)  # 단건
def readbyspendid(
    userId: int = Path(...),
    spendId: int = Path(...),
    db: Session = Depends(get_db)
):
    result = record_service.records_readbyspendid(db=db, user_id=userId, spend_id=spendId)
    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result

# 소비내역 수정 API
@router.put("/edit/{spendId}", response_model=RecordsRead)
def records_edit(
    spendId: int = Path(...),
    edited_data: RecordsEdit = Body(...),
    db: Session = Depends(get_db)
):
    edited_record = record_service.records_edit(db, spendId, edited_data)
    if edited_record is None:
        raise HTTPException(status_code=404, detail="수정할 소비내역을 찾을 수 없습니다.")
    if edited_record == "not_change":
        raise HTTPException(status_code=400, detail="변경된 내용이 없습니다.")
    return edited_record

# 소비내역 삭제 API
@router.delete("/delete/{spendId}")
def records_delete(
    spendId: int = Path(...),
    db: Session = Depends(get_db)
):
    success = record_service.records_delete(db, spendId)
    if not success:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return {"message": "소비내역이 삭제되었습니다."}