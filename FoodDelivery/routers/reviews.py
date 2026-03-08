from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderStatus
from models.review import Review
from models.restaurant import Restaurant
from models.user import UserRole
from schemas.order import ReviewCreate, ReviewOut
from routers.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewOut)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != UserRole.customer:
        raise HTTPException(status_code=403, detail="只有顾客可以评价")

    order = db.query(Order).filter(
        Order.id == data.order_id,
        Order.customer_id == current_user.id,
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.completed:
        raise HTTPException(status_code=400, detail="订单未完成，无法评价")

    existing = db.query(Review).filter(Review.order_id == data.order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="已经评价过了")

    review = Review(
        order_id=data.order_id,
        customer_id=current_user.id,
        restaurant_id=order.restaurant_id,
        rider_id=order.rider_id,
        restaurant_rating=data.restaurant_rating,
        rider_rating=data.rider_rating,
        comment=data.comment,
    )
    db.add(review)

    # Update restaurant average rating
    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    total = restaurant.rating * restaurant.rating_count + data.restaurant_rating
    restaurant.rating_count += 1
    restaurant.rating = round(total / restaurant.rating_count, 1)

    db.commit()
    db.refresh(review)
    return review


@router.get("/{restaurant_id}", response_model=List[ReviewOut])
def list_reviews(restaurant_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Review)
        .filter(Review.restaurant_id == restaurant_id)
        .order_by(Review.created_at.desc())
        .limit(50)
        .all()
    )
