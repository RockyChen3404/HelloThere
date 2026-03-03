from typing import Optional
from pydantic import BaseModel, EmailStr
from models.user import UserRole


class UserRegister(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    password: str
    role: UserRole = UserRole.customer
    address: Optional[str] = None


class UserLogin(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    email: Optional[str]
    role: UserRole
    address: Optional[str]

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
