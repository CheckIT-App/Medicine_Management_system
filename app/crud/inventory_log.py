from sqlalchemy.orm import Session
from app.models import InventoryLog
from app.schemas.inventory_log import InventoryLogCreate


def create_inventory_log(db: Session, log: InventoryLogCreate):
    db_log = InventoryLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_inventory_log_by_id(db: Session, log_id: int):
    return db.query(InventoryLog).filter(InventoryLog.id == log_id).first()


def get_all_inventory_logs(db: Session):
    return db.query(InventoryLog).all()
