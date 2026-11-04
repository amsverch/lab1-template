from typing import Optional

from pydantic import BaseModel, ConfigDict


class PersonCreate(BaseModel):
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None


class PersonResponse(BaseModel):
    id: int
    name: str
    age: Optional[int] = None
    address: Optional[str] = None
    work: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)