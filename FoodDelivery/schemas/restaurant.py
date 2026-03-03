from typing import Optional
from pydantic import BaseModel


class RestaurantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    cuisine_type: Optional[str] = None
    delivery_fee: float = 0.0
    min_order: float = 0.0
    image: Optional[str] = None


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    cuisine_type: Optional[str] = None
    delivery_fee: Optional[float] = None
    min_order: Optional[float] = None
    is_open: Optional[bool] = None
    image: Optional[str] = None


class RestaurantOut(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    address: str
    cuisine_type: Optional[str]
    rating: float
    rating_count: int
    delivery_fee: float
    min_order: float
    is_open: bool
    image: Optional[str]

    model_config = {"from_attributes": True}
