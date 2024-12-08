from __future__ import annotations  # Enable forward references
from pydantic import BaseModel
from datetime import date
from typing import Optional, List


# Base schema for shared fields
class MedicineTypeBase(BaseModel):
    barcode: str
    name: str
    description: Optional[str]
    size_id: int
    x: int
    y: int

    class Config:
        orm_mode = True  # Enables compatibility with SQLAlchemy ORM


# Schema for creation requests
class MedicineTypeCreate(MedicineTypeBase):
    pass


# Schema for updates (all fields optional for partial updates)
class MedicineTypeUpdate(BaseModel):
    barcode: Optional[str]
    name: Optional[str]
    description: Optional[str]
    size_id: Optional[int]
    x: Optional[int]
    y: Optional[int]

    class Config:
        orm_mode = True


# Schema for instances (base and for creation/response)
class MedicineInstanceBase(BaseModel):
    batch_number: str
    quantity: int
    expiration_date: date

    class Config:
        orm_mode = True


# Schema for instance creation requests
class MedicineInstanceCreate(MedicineInstanceBase):
    medicine_type_id: int  # Foreign key to MedicineType


# Schema for response serialization of MedicineInstance
class MedicineInstanceResponse(MedicineInstanceBase):
    id: int
    medicine_type: Optional[MedicineTypeResponse]  # Prevent circular dependency


# Response schema for MedicineType
class MedicineTypeResponse(MedicineTypeBase):
    id: int
   # instances: Optional[List[MedicineInstanceResponse]] = []  # Nested instance data
