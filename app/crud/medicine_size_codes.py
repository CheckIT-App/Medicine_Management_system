from sqlalchemy.orm import Session
from app.models import MedicineSizeCode

def get_all_medicine_size_codes(db: Session):
    return db.query(MedicineSizeCode).all()
