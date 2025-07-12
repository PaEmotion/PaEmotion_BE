from sqlalchemy.orm import Session
from models.record import Record
from schemas.record import RecordsCreate, RecordsDelete, RecordsRead, RecordsEdit
from datetime import datetime, date
from sqlalchemy import Date

# 생성된 새로운 소비 내역을 DB에 저장하는 함수
def records_create(db: Session, record_data: RecordsCreate) -> Record:
    new_record = Record(**record_data.dict(by_alias=True))
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

# 소비내역 수정 함수
def records_readbydate(db: Session, user_id: int, target_date: date, spend_id: int):
    return db.query(Record).filter(
        Record.userId == user_id,
        Record.spendDate.cast(Date) == target_date,
        Record.spendId == spend_id
    ).first()

# DB에서 소비내역을 수정하는 함수
def records_edit(db: Session, spendId: int, record_update: RecordsEdit) -> Record | None:
    record = db.query(Record).filter(Record.spendId == spendId).first()
    if not record:
        return None

    update_data = record_update.model_dump(exclude_unset=True, by_alias=True)

    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

# DB에서 소비내역을 삭제하는 함수
def records_delete(db: Session, spendId: int) -> bool:
    record = db.query(Record).filter(Record.spendId == spendId).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True