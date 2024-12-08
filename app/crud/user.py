from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from app.models import User
from app.schemas.user import UserCreate


def create_user(db: Session, user_data: UserCreate):
    """Create a new user in the database."""
    db_user = User(**user_data.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_all_users(db: Session):
    """Retrieve all users from the database."""
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    """Retrieve a single user by their ID."""
    try:
        return db.query(User).filter(User.id == user_id).one()
    except NoResultFound:
        return None

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def delete_user(db: Session, user_id: int):
    """Delete a user by their ID."""
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


def update_user(db: Session, user_id: int, updated_data: dict):
    """
    Update an existing user's details.
    :param db: Database session
    :param user_id: ID of the user to update
    :param updated_data: Dictionary containing fields to update
    """
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    # Update only the provided fields
    for key, value in updated_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user
