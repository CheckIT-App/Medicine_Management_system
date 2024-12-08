from pydantic import BaseModel

class GenderCodeBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class MedicineSizeCodeBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class RoleCodeBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
