from typing import Optional
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    restaurant_id: int
    name: str
    sort_order: int = 0


class CategoryOut(BaseModel):
    id: int
    restaurant_id: int
    name: str
    sort_order: int

    model_config = {"from_attributes": True}


class MenuItemCreate(BaseModel):
    restaurant_id: int
    category_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    image: Optional[str] = None
    is_available: bool = True


class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    is_available: Optional[bool] = None
    category_id: Optional[int] = None


class MenuItemOut(BaseModel):
    id: int
    restaurant_id: int
    category_id: Optional[int]
    name: str
    description: Optional[str]
    price: float
    image: Optional[str]
    is_available: bool
    sales_count: int

    model_config = {"from_attributes": True}
