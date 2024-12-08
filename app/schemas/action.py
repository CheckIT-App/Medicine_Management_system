from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict


class ActionBase(BaseModel):
    action_type: str
    details: Optional[Dict]

    class Config:
        orm_mode = True


class ActionCreate(ActionBase):
    user_id: Optional[int]


class ActionResponse(ActionBase):
    id: int
    action_date: datetime
    user_id: Optional[int]
