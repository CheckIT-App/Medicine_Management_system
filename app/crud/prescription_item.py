from typing import List
from sqlalchemy.orm import Session
from app.models import PrescriptionItem
from app.schemas.prescription_item import PrescriptionItemCreate


def create_prescription_item(db: Session, item: PrescriptionItemCreate):
    db_item = PrescriptionItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# def add_prescription_items(db: Session, items: List[PrescriptionItemCreate]) -> None:
#     """
#     Adds a list of prescription items to the database.

#     Args:
#         db (Session): Database session.
#         items (List[PrescriptionItemCreate]): List of prescription item data to add.

#     Returns:
#         None
#     """
#     # Convert the input data into database model instances
#     db_items = [
#         PrescriptionItem(
#             prescription_id=item.prescription_id,
#             medicine_id=item.medicine_id,
#             quantity=item.quantity
#         )
#         for item in items
#     ]

#     # Add all the items to the session in a batch
#     db.bulk_save_objects(db_items)
#     db.commit()

def get_prescription_item_by_id(db: Session, item_id: int):
    return db.query(PrescriptionItem).filter(PrescriptionItem.id == item_id).first()


def get_all_prescription_items(db: Session):
    return db.query(PrescriptionItem).all()
