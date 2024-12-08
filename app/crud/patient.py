from sqlalchemy.orm import Session
from app.models import Patient
from app.schemas.patient import PatientCreate


def create_patient(db: Session, patient: PatientCreate):
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def get_all_patients(db: Session):
    return db.query(Patient).all()


def get_patient_by_id(db: Session, patient_id: int):
    return db.query(Patient).filter(Patient.id == patient_id).first()


def update_patient(db: Session, patient_id: int, updated_data: dict):
    db.query(Patient).filter(Patient.id == patient_id).update(updated_data)
    db.commit()


def delete_patient(db: Session, patient_id: int):
    patient = get_patient_by_id(db, patient_id)
    if patient:
        db.delete(patient)
        db.commit()