from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.restaurant import Restaurant
from models.user import UserRole
from schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantOut
from routers.auth import get_current_user

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/", response_model=List[RestaurantOut])
def list_restaurants(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Restaurant).filter(Restaurant.is_open == True)
    if search:
        q = q.filter(Restaurant.name.contains(search))
    return q.order_by(Restaurant.rating.desc()).all()


@router.get("/{restaurant_id}", response_model=RestaurantOut)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="餐厅不存在")
    return r


@router.post("/", response_model=RestaurantOut)
def create_restaurant(
    data: RestaurantCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != UserRole.merchant:
        raise HTTPException(status_code=403, detail="只有商家可以创建餐厅")
    r = Restaurant(owner_id=current_user.id, **data.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/{restaurant_id}", response_model=RestaurantOut)
def update_restaurant(
    restaurant_id: int,
    data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    r = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="餐厅不存在")
    if r.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限修改此餐厅")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(r, field, value)
    db.commit()
    db.refresh(r)
    return r


@router.get("/mine/list", response_model=List[RestaurantOut])
def my_restaurants(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Restaurant).filter(Restaurant.owner_id == current_user.id).all()
