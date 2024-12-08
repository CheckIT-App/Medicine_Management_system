from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    first_name: str  # New field
    last_name: str   # New field
    identity_number: str  # New field
    email: str
    role_id: int

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
