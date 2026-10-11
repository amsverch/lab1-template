from pydantic import BaseModel
from typing import Optional

class PersonCreate(BaseModel):
    name: str
    age: Optional[int] = None

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

class PersonResponse(BaseModel):
    id: int
    name: str
    age: Optional[int]

    class Config:
        from_attributes = True
