from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from models.order import OrderStatus


class CartItemAdd(BaseModel):
    menu_item_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    menu_item_id: int
    restaurant_id: int
    quantity: int
    name: str
    price: float
    subtotal: float

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    delivery_address: str
    note: Optional[str] = None


class OrderItemOut(BaseModel):
    id: int
    menu_item_id: int
    name: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderOut(BaseModel):
    id: int
    customer_id: int
    restaurant_id: int
    rider_id: Optional[int]
    delivery_address: str
    note: Optional[str]
    total_price: float
    delivery_fee: float
    status: OrderStatus
    status_label: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    order_id: int
    restaurant_rating: float
    rider_rating: Optional[float] = None
    comment: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    order_id: int
    customer_id: int
    restaurant_id: int
    restaurant_rating: float
    rider_rating: Optional[float]
    comment: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
