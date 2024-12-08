from typing import List
from sqlalchemy.orm import Session
from app.models import MedicineType, MedicineInstance
from app.schemas.medicine import MedicineTypeCreate, MedicineInstanceCreate, MedicineTypeResponse


# CRUD for MedicineType
def get_all_medicine_types(db: Session) -> List[MedicineTypeResponse]:
    """
    Fetch all medicine types from the database.
    """
    return db.query(MedicineType).all()


def get_medicine_type_by_id(db: Session, medicine_id: int):
    """
    Fetch a single medicine type by its ID.
    """
    return db.query(MedicineType).filter(MedicineType.id == medicine_id).first()


def create_medicine_type(db: Session, medicine_data: MedicineTypeCreate):
    """
    Create a new medicine type in the database.
    """
    new_medicine = MedicineType(**medicine_data.dict())
    db.add(new_medicine)
    db.commit()
    db.refresh(new_medicine)
    return new_medicine


def update_medicine_type(db: Session, medicine_id: int, updated_data: dict):
    """
    Update an existing medicine type with the given data.
    """
    medicine = get_medicine_type_by_id(db, medicine_id)
    if not medicine:
        return None
    for key, value in updated_data.items():
        setattr(medicine, key, value)
    db.commit()
    db.refresh(medicine)
    return medicine


def delete_medicine_type(db: Session, medicine_id: int):
    """
    Delete a medicine type by its ID.
    """
    medicine = get_medicine_type_by_id(db, medicine_id)
    if medicine:
        db.delete(medicine)
        db.commit()
        
# CRUD for MedicineInstance
def create_medicine_instance(db: Session, instance: MedicineInstanceCreate):
    db_instance = MedicineInstance(**instance.dict())
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    return db_instance


def get_medicine_instance_by_id(db: Session, instance_id: int):
    return db.query(MedicineInstance).filter(MedicineInstance.id == instance_id).first()


def get_all_medicine_instances(db: Session):
    return db.query(MedicineInstance).all()
