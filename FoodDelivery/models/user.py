from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum
from database import Base
import enum


class UserRole(str, enum.Enum):
    customer = "customer"
    merchant = "merchant"
    rider = "rider"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.customer)
    address = Column(String(200), nullable=True)
    avatar = Column(String(300), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
