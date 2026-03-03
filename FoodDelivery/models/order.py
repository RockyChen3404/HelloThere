from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"        # 待接单
    accepted = "accepted"      # 已接单
    preparing = "preparing"    # 制作中
    ready = "ready"            # 待取餐
    delivering = "delivering"  # 配送中
    delivered = "delivered"    # 已送达
    completed = "completed"    # 已完成
    cancelled = "cancelled"    # 已取消


STATUS_LABEL = {
    OrderStatus.pending: "待接单",
    OrderStatus.accepted: "已接单",
    OrderStatus.preparing: "制作中",
    OrderStatus.ready: "待取餐",
    OrderStatus.delivering: "配送中",
    OrderStatus.delivered: "已送达",
    OrderStatus.completed: "已完成",
    OrderStatus.cancelled: "已取消",
}


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    rider_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    delivery_address = Column(String(300), nullable=False)
    note = Column(String(200), nullable=True)
    total_price = Column(Float, nullable=False)
    delivery_fee = Column(Float, default=0.0)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    name = Column(String(100), nullable=False)  # snapshot at order time
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # snapshot at order time


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
