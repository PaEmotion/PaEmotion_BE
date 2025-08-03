from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from db.session import get_db
from schemas.record import RecordsCreate, RecordsRead, RecordsEdit
from services.record import record as record_service
from auth.jwt_token import get_current_user
from models import User

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/create", response_model=RecordsRead)
def create_records(
    record: RecordsCreate,
    db: Session = Depends(get_db)
):
    new_record = record_service.create_records(db, record)
    return new_record


@router.get("/me", response_model=List[RecordsRead])
def readbydate_records(
    startDate: Optional[date] = Query(None),
    endDate: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not startDate or not endDate:
        raise HTTPException(status_code=400, detail="startDate와 endDate를 모두 입력해야 합니다.")
    
    result = record_service.readbydate_records(
        db=db,
        user_id=current_user.userId,
        start_date=startDate,
        end_date=endDate
    )

    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result


@router.get("/me/{spendId}", response_model=RecordsRead)
def read_records(
    spendId: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = record_service.read_records(
        db=db,
        user_id=current_user.userId,
        spend_id=spendId
    )
    if not result:
        raise HTTPException(status_code=404, detail="소비내역을 찾을 수 없습니다.")
    return result


@router.put("/me/{spendId}", response_model=RecordsRead)
def edit_records(
    spendId: int = Path(...),
    edited_data: RecordsEdit = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = record_service.read_records(db, current_user.userId, spendId)
    if not target:
        raise HTTPException(status_code=404, detail="수정할 소비내역을 찾을 수 없습니다.")
    
    edited_record = record_service.edit_records(db, spendId, edited_data)
    if edited_record == "not_change":
        raise HTTPException(status_code=400, detail="변경된 내용이 없습니다.")
    
    return edited_record


@router.delete("/me/{spendId}")
def delete_records(
    spendId: int = Path(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target = record_service.read_records(db, current_user.userId, spendId)
    if not target:
        raise HTTPException(status_code=404, detail="삭제할 소비내역을 찾을 수 없습니다.")
    
    success = record_service.delete_records(db, spendId)
    return {"message": "소비내역이 삭제되었습니다."}