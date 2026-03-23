from pydantic import BaseModel, Field
from typing import Optional

class UserBase(BaseModel):
    username: str
    role: Optional[str] = "customer"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str