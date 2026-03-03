from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    address = Column(String(200), nullable=False)
    cuisine_type = Column(String(50), nullable=True)
    rating = Column(Float, default=5.0)
    rating_count = Column(Integer, default=0)
    delivery_fee = Column(Float, default=0.0)
    min_order = Column(Float, default=0.0)
    is_open = Column(Boolean, default=True)
    image = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
