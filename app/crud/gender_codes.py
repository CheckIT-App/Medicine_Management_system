from sqlalchemy.orm import Session
from app.models import GenderCode

def get_all_gender_codes(db: Session):
    return db.query(GenderCode).all()