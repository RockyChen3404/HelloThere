from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import Order, OrderItem, CartItem, OrderStatus, STATUS_LABEL
from models.menu import MenuItem
from models.restaurant import Restaurant
from models.user import UserRole
from schemas.order import OrderCreate, OrderOut, OrderItemOut, OrderStatusUpdate
from routers.auth import get_current_user
from services.order import can_transition

router = APIRouter(prefix="/orders", tags=["orders"])


def _order_to_out(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        customer_id=order.customer_id,
        restaurant_id=order.restaurant_id,
        rider_id=order.rider_id,
        delivery_address=order.delivery_address,
        note=order.note,
        total_price=order.total_price,
        delivery_fee=order.delivery_fee,
        status=order.status,
        status_label=STATUS_LABEL.get(order.status, order.status),
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.post("/", response_model=OrderOut)
def create_order(
    data: OrderCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != UserRole.customer:
        raise HTTPException(status_code=403, detail="只有顾客可以下单")

    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车为空")

    restaurant = db.query(Restaurant).filter(
        Restaurant.id == cart_items[0].restaurant_id
    ).first()

    subtotal = 0.0
    for ci in cart_items:
        mi = db.query(MenuItem).filter(MenuItem.id == ci.menu_item_id).first()
        if not mi or not mi.is_available:
            raise HTTPException(status_code=400, detail=f"菜品 {mi.name if mi else ci.menu_item_id} 已下架")
        subtotal += mi.price * ci.quantity

    total = round(subtotal + restaurant.delivery_fee, 2)

    order = Order(
        customer_id=current_user.id,
        restaurant_id=restaurant.id,
        delivery_address=data.delivery_address,
        note=data.note,
        total_price=total,
        delivery_fee=restaurant.delivery_fee,
        status=OrderStatus.pending,
    )
    db.add(order)
    db.flush()

    for ci in cart_items:
        mi = db.query(MenuItem).filter(MenuItem.id == ci.menu_item_id).first()
        oi = OrderItem(
            order_id=order.id,
            menu_item_id=ci.menu_item_id,
            name=mi.name,
            quantity=ci.quantity,
            unit_price=mi.price,
        )
        db.add(oi)
        mi.sales_count += ci.quantity

    # Clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    db.refresh(order)
    return _order_to_out(order)


@router.get("/", response_model=List[OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == UserRole.customer:
        orders = db.query(Order).filter(
            Order.customer_id == current_user.id
        ).order_by(Order.created_at.desc()).all()
    elif current_user.role == UserRole.merchant:
        my_restaurants = db.query(Restaurant).filter(
            Restaurant.owner_id == current_user.id
        ).all()
        ids = [r.id for r in my_restaurants]
        orders = db.query(Order).filter(
            Order.restaurant_id.in_(ids)
        ).order_by(Order.created_at.desc()).all()
    elif current_user.role == UserRole.rider:
        orders = db.query(Order).filter(
            (Order.rider_id == current_user.id) |
            (Order.status == OrderStatus.ready)
        ).order_by(Order.created_at.desc()).all()
    else:
        orders = []
    return [_order_to_out(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return _order_to_out(order)


@router.get("/{order_id}/items", response_model=List[OrderItemOut])
def get_order_items(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    return [
        OrderItemOut(
            id=i.id,
            menu_item_id=i.menu_item_id,
            name=i.name,
            quantity=i.quantity,
            unit_price=i.unit_price,
            subtotal=round(i.unit_price * i.quantity, 2),
        )
        for i in items
    ]


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    if not can_transition(order.status, data.status, current_user.role):
        raise HTTPException(
            status_code=400,
            detail=f"不允许从 {STATUS_LABEL[order.status]} 切换到 {STATUS_LABEL[data.status]}"
        )

    # Assign rider when they pick up the order
    if data.status == OrderStatus.delivering and current_user.role == UserRole.rider:
        order.rider_id = current_user.id

    order.status = data.status

    # Update restaurant rating after completion is triggered by review
    db.commit()
    db.refresh(order)
    return _order_to_out(order)
