from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PatientBase(BaseModel):
    first_name: str
    last_name: str
    identity_number: str
    age: int
    gender_id: int
    contact_info: Optional[str]

    class Config:
        orm_mode = True


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    created_at: datetime
