from pydantic import BaseModel


class PrescriptionItemBase(BaseModel):
    quantity: int

    class Config:
        orm_mode = True


class PrescriptionItemCreate(PrescriptionItemBase):
    prescription_id: int
    medicine_id: int


class PrescriptionItemResponse(PrescriptionItemBase):
    id: int
    prescription_id: int
    medicine_id: int
