from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.menu import Category, MenuItem
from models.restaurant import Restaurant
from schemas.menu import (
    CategoryCreate, CategoryOut,
    MenuItemCreate, MenuItemUpdate, MenuItemOut,
)
from routers.auth import get_current_user

router = APIRouter(prefix="/menu", tags=["menu"])


# ---- Categories ----

@router.get("/{restaurant_id}/categories", response_model=List[CategoryOut])
def list_categories(restaurant_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Category)
        .filter(Category.restaurant_id == restaurant_id)
        .order_by(Category.sort_order)
        .all()
    )


@router.post("/categories", response_model=CategoryOut)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    r = db.query(Restaurant).filter(Restaurant.id == data.restaurant_id).first()
    if not r or r.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ---- Menu Items ----

@router.get("/{restaurant_id}/items", response_model=List[MenuItemOut])
def list_items(restaurant_id: int, db: Session = Depends(get_db)):
    return (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True)
        .all()
    )


@router.post("/items", response_model=MenuItemOut)
def create_item(
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    r = db.query(Restaurant).filter(Restaurant.id == data.restaurant_id).first()
    if not r or r.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/items/{item_id}", response_model=MenuItemOut)
def update_item(
    item_id: int,
    data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="菜品不存在")
    r = db.query(Restaurant).filter(Restaurant.id == item.restaurant_id).first()
    if r.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="菜品不存在")
    r = db.query(Restaurant).filter(Restaurant.id == item.restaurant_id).first()
    if r.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限")
    db.delete(item)
    db.commit()
    return {"message": "已删除"}
