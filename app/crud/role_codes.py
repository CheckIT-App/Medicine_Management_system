from sqlalchemy.orm import Session
from app.models import RoleCode

def get_all_role_codes(db: Session):
    return db.query(RoleCode).all()