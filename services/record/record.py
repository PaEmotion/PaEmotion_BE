from sqlalchemy.orm import Session
from models.record import Record
from schemas.record import RecordsCreate, RecordsEdit
from datetime import date

def create_records(db: Session, record_data: RecordsCreate) -> Record: 
    new_record = Record(**record_data.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

# 기간 조회
def readbydate_records(db: Session, user_id: int, start_date: date, end_date: date): 
    return (
        db.query(Record)
        .filter(
            Record.userId == user_id,
            Record.spendDate >= start_date,
            Record.spendDate <= end_date
        )
        .all()
    )

# 단건 조회
def read_records(db: Session, user_id: int, spend_id: int): 
    return db.query(Record).filter_by(userId=user_id, spendId=spend_id).first()

def edit_records(db: Session, spend_id: int, edited_data: RecordsEdit) -> Record | None | str:
    target_record = db.query(Record).filter(Record.spendId == spend_id).first()
    if not target_record: return None

    new_edited_data = edited_data.model_dump(exclude_unset=True)

    is_changed = False
    for key, new_value in new_edited_data.items():
        old_value = getattr(target_record, key, None)
        if new_value != old_value:
            setattr(target_record, key, new_value)
            is_changed = True
    if not is_changed: return "not_change"

    db.commit()
    db.refresh(target_record)
    return target_record

def delete_records(db: Session, spend_id: int) -> bool:
    target_record = db.query(Record).filter(Record.spendId == spend_id).first()
    if not target_record:
        return False
    db.delete(target_record)
    db.commit()
    return True