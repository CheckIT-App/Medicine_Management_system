from sqlalchemy.orm import Session
from app.models import Action
from app.schemas.action import ActionCreate


def create_action(db: Session, action: ActionCreate):
    db_action = Action(**action.dict())
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


def get_action_by_id(db: Session, action_id: int):
    return db.query(Action).filter(Action.id == action_id).first()


def get_all_actions(db: Session):
    return db.query(Action).all()
