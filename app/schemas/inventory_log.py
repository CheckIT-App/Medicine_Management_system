from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class InventoryLogBase(BaseModel):
    action_type: str
    quantity_change: int

    class Config:
        orm_mode = True


class InventoryLogCreate(InventoryLogBase):
    medicine_id: int
    performed_by: Optional[int]


class InventoryLogResponse(InventoryLogBase):
    id: int
    action_date: datetime
    medicine_id: int
    performed_by: Optional[int]
