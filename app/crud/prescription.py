from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import NoResultFound
from typing import List, Optional
from app.models import Prescription, PrescriptionItem
from app.schemas.prescription import PrescriptionCreate, PrescriptionResponse
from app.schemas.prescription_item import PrescriptionItemCreate
def create_prescription(db: Session, prescription: PrescriptionCreate) -> Prescription:
    """
    Create a new prescription.
    """
    new_prescription = Prescription(**prescription.dict())
    db.add(new_prescription)
    db.commit()
    db.refresh(new_prescription)
    return new_prescription


def get_all_prescriptions(db: Session) -> List[PrescriptionResponse]:
    """
    Get a list of all prescriptions.
    """
    return db.query(Prescription).all()


def get_prescription_by_id(db: Session, prescription_id: int):
    # Fetch the prescription and its related items
    prescription = (
        db.query(Prescription)
        .filter(Prescription.id == prescription_id)
        .options(joinedload(Prescription.prescription_items))
        .first()
    )

    if not prescription:
        return None

    # Populate medicines list
    medicines = [
        {
            "quantity": item.quantity,
            "id":item.medicine_id
        }
        for item in prescription.prescription_items
    ]

    # Convert to dictionary and include medicines
    response_data = {
        "id": prescription.id,
        "patient_id": prescription.patient_id,
        "prescribed_by": prescription.prescribed_by,
        "created_at": prescription.created_at,
        "medicines": medicines,
    }

    return response_data

def update_prescription(db: Session, prescription_id: int, updated_data: dict) -> Prescription:
    """
    Update an existing prescription by ID.
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise ValueError("Prescription not found")

    for key, value in updated_data.items():
        if hasattr(prescription, key):
            setattr(prescription, key, value)

    db.commit()
    db.refresh(prescription)
    return prescription

def delete_prescription(db: Session, prescription_id: int) -> None:
    """
    Delete a prescription by its ID.
    """
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()

    if not prescription:
        raise ValueError("Prescription not found")

    # Delete associated prescription items
    db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription_id).delete()

    db.delete(prescription)
    db.commit()


# def add_prescription_items(db: Session, items: List[PrescriptionItemCreate]) -> None:
#     """
#     Add multiple prescription items to a prescription.
#     """
#     db_items = [PrescriptionItem(**item.dict()) for item in items]
#     db.add_all(db_items)
#     db.commit()

def add_prescription_items(db: Session, items: list[PrescriptionItemCreate]) -> None:
    """
    Add prescription items to the database.
    """
    db.bulk_save_objects(
        [
            PrescriptionItem(
                prescription_id=item.prescription_id,
                medicine_id=item.medicine_id,
                quantity=item.quantity,
            )
            for item in items
        ]
    )
    db.commit()
def delete_prescription_items(db: Session, prescription_id: int) -> None:
    """
    Delete all prescription items for a given prescription ID.
    """
    db.query(PrescriptionItem).filter(PrescriptionItem.prescription_id == prescription_id).delete()
    db.commit()    