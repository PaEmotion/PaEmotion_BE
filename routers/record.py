from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from schemas.record import RecordsCreate, RecordsRead, RecordsDelete, RecordsEdit
from db.session import get_db
from services import record as record_service

router = APIRouter(prefix="/records", tags=["records"])

# 소비내역 생성 API
@router.post("/create", response_model=RecordsRead)
def records_create(record: RecordsCreate, db: Session = Depends(get_db)):
    new_record = record_service.create_record(db, record)
    return new_record

# 유저별 특정 날짜의 특정 소비내역 단건 조회 API
@router.get("/readbydate/{userId}/{target_date}/{spendId}", response_model=RecordsRead)
def records_readbydate(userId: int, target_date: date, spendId: int, db: Session = Depends(get_db)):
    record = record_service.get_record_by_user_date_and_id(db, userId, target_date, spendId)
    if not record:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return record

# 소비내역 수정 API
@router.put("/edit/{spendId}", response_model=RecordsRead)
def records_edit(spendId: int, record_update: RecordsEdit, db: Session = Depends(get_db)):
    edited_record = record_service.edit_record(db, spendId, record_update)
    if not edited_record:
        raise HTTPException(status_code=404, detail="수정할 소비내역을 찾을 수 없습니다.")
    return edited_record

# 소비내역 삭제 API
@router.delete("/delete/{spendId}")
def records_delete(spendId: int, db: Session = Depends(get_db)):
    success = record_service.delete_record(db, spendId)
    if not success:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return {"message": "소비내역이 삭제되었습니다."}