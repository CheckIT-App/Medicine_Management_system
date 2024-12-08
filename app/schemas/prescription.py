from typing import List, Optional
from app.schemas.prescription_item import PrescriptionItemResponse
from pydantic import BaseModel
from datetime import datetime


class PrescriptionBase(BaseModel):
    pass


class PrescriptionCreate(PrescriptionBase):
    patient_id: int
    prescribed_by: Optional[int]

    class Config:
        orm_mode = True


class PrescriptionMedicineResponse(BaseModel):
    
    quantity: int
    id:int

class PrescriptionResponse(BaseModel):
    id: int
    patient_id: int
    prescribed_by: int
    created_at: datetime
    medicines: List[PrescriptionMedicineResponse]  # List of medicines with their details

    class Config:
        orm_mode = True
