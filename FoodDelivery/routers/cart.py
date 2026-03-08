from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.order import CartItem
from models.menu import MenuItem
from schemas.order import CartItemAdd, CartItemOut
from routers.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


def _build_cart_out(item: CartItem, db: Session) -> CartItemOut:
    menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
    return CartItemOut(
        id=item.id,
        menu_item_id=item.menu_item_id,
        restaurant_id=item.restaurant_id,
        quantity=item.quantity,
        name=menu_item.name if menu_item else "已下架",
        price=menu_item.price if menu_item else 0,
        subtotal=round((menu_item.price if menu_item else 0) * item.quantity, 2),
    )


@router.get("/", response_model=List[CartItemOut])
def get_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    return [_build_cart_out(i, db) for i in items]


@router.post("/items", response_model=CartItemOut)
def add_to_cart(
    data: CartItemAdd,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    menu_item = db.query(MenuItem).filter(MenuItem.id == data.menu_item_id).first()
    if not menu_item or not menu_item.is_available:
        raise HTTPException(status_code=404, detail="菜品不存在或已下架")

    # Clear cart if from a different restaurant
    existing_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if existing_items and existing_items[0].restaurant_id != menu_item.restaurant_id:
        for old in existing_items:
            db.delete(old)

    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.menu_item_id == data.menu_item_id,
    ).first()

    if cart_item:
        cart_item.quantity += data.quantity
    else:
        cart_item = CartItem(
            user_id=current_user.id,
            menu_item_id=data.menu_item_id,
            restaurant_id=menu_item.restaurant_id,
            quantity=data.quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return _build_cart_out(cart_item, db)


@router.put("/items/{item_id}", response_model=CartItemOut)
def update_cart_item(
    item_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    if quantity <= 0:
        db.delete(cart_item)
        db.commit()
        return {"message": "已移除"}
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    return _build_cart_out(cart_item, db)


@router.delete("/items/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id, CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    db.delete(cart_item)
    db.commit()
    return {"message": "已移除"}


@router.delete("/")
def clear_cart(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()
    return {"message": "购物车已清空"}
