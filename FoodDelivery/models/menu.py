from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(50), nullable=False)
    sort_order = Column(Integer, default=0)


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(String(300), nullable=True)
    price = Column(Float, nullable=False)
    image = Column(String(300), nullable=True)
    is_available = Column(Boolean, default=True)
    sales_count = Column(Integer, default=0)
