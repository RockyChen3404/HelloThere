"""HTML page routes rendered with Jinja2."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from models.restaurant import Restaurant
from models.menu import Category, MenuItem
from models.order import Order, CartItem, OrderStatus, STATUS_LABEL
from models.review import Review
from routers.auth import get_current_user_optional, get_current_user

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    search: str = "",
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    q = db.query(Restaurant)
    if search:
        q = q.filter(Restaurant.name.contains(search))
    restaurants = q.order_by(Restaurant.rating.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "restaurants": restaurants, "search": search, "user": current_user},
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/restaurant/{restaurant_id}", response_class=HTMLResponse)
def restaurant_detail(
    restaurant_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        return RedirectResponse("/")
    categories = (
        db.query(Category)
        .filter(Category.restaurant_id == restaurant_id)
        .order_by(Category.sort_order)
        .all()
    )
    items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id, MenuItem.is_available == True)
        .all()
    )
    reviews = (
        db.query(Review)
        .filter(Review.restaurant_id == restaurant_id)
        .order_by(Review.created_at.desc())
        .limit(10)
        .all()
    )
    return templates.TemplateResponse(
        "restaurant/detail.html",
        {
            "request": request,
            "restaurant": restaurant,
            "categories": categories,
            "items": items,
            "reviews": reviews,
            "user": current_user,
        },
    )


@router.get("/cart", response_class=HTMLResponse)
def cart_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    if not current_user:
        return RedirectResponse("/login")
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    enriched = []
    total = 0.0
    restaurant = None
    for ci in cart_items:
        mi = db.query(MenuItem).filter(MenuItem.id == ci.menu_item_id).first()
        if mi:
            subtotal = mi.price * ci.quantity
            total += subtotal
            enriched.append({
                "id": ci.id,
                "menu_item_id": ci.menu_item_id,
                "name": mi.name,
                "price": mi.price,
                "quantity": ci.quantity,
                "subtotal": round(subtotal, 2),
                "restaurant_id": ci.restaurant_id,
            })
            if not restaurant:
                restaurant = db.query(Restaurant).filter(
                    Restaurant.id == ci.restaurant_id
                ).first()
    delivery_fee = restaurant.delivery_fee if restaurant else 0
    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart_items": enriched,
            "total": round(total, 2),
            "delivery_fee": delivery_fee,
            "grand_total": round(total + delivery_fee, 2),
            "restaurant": restaurant,
            "user": current_user,
            "address": current_user.address or "",
        },
    )


@router.get("/orders", response_class=HTMLResponse)
def orders_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    if not current_user:
        return RedirectResponse("/login")
    orders = (
        db.query(Order)
        .filter(Order.customer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    restaurants = {r.id: r for r in db.query(Restaurant).all()}
    return templates.TemplateResponse(
        "orders/list.html",
        {
            "request": request,
            "orders": orders,
            "restaurants": restaurants,
            "STATUS_LABEL": STATUS_LABEL,
            "user": current_user,
        },
    )


@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail(
    order_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    if not current_user:
        return RedirectResponse("/login")
    from models.order import OrderItem
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return RedirectResponse("/orders")
    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    restaurant = db.query(Restaurant).filter(Restaurant.id == order.restaurant_id).first()
    has_review = db.query(Review).filter(Review.order_id == order_id).first() is not None
    return templates.TemplateResponse(
        "orders/detail.html",
        {
            "request": request,
            "order": order,
            "order_items": items,
            "restaurant": restaurant,
            "STATUS_LABEL": STATUS_LABEL,
            "OrderStatus": OrderStatus,
            "user": current_user,
            "has_review": has_review,
        },
    )


@router.get("/dashboard/merchant", response_class=HTMLResponse)
def merchant_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    if not current_user or current_user.role != "merchant":
        return RedirectResponse("/login")
    from models.user import UserRole
    restaurants = db.query(Restaurant).filter(
        Restaurant.owner_id == current_user.id
    ).all()
    rest_ids = [r.id for r in restaurants]
    orders = (
        db.query(Order)
        .filter(Order.restaurant_id.in_(rest_ids))
        .order_by(Order.created_at.desc())
        .limit(50)
        .all()
    )
    all_items = {}
    for rest in restaurants:
        all_items[rest.id] = (
            db.query(MenuItem).filter(MenuItem.restaurant_id == rest.id).all()
        )
    categories = {}
    for rest in restaurants:
        categories[rest.id] = (
            db.query(Category).filter(Category.restaurant_id == rest.id).all()
        )
    return templates.TemplateResponse(
        "dashboard/merchant.html",
        {
            "request": request,
            "user": current_user,
            "restaurants": restaurants,
            "orders": orders,
            "menu_items": all_items,
            "categories": categories,
            "STATUS_LABEL": STATUS_LABEL,
            "OrderStatus": OrderStatus,
        },
    )


@router.get("/dashboard/rider", response_class=HTMLResponse)
def rider_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    if not current_user or current_user.role != "rider":
        return RedirectResponse("/login")
    available = (
        db.query(Order)
        .filter(Order.status == OrderStatus.ready)
        .order_by(Order.created_at)
        .all()
    )
    my_orders = (
        db.query(Order)
        .filter(Order.rider_id == current_user.id)
        .order_by(Order.created_at.desc())
        .limit(20)
        .all()
    )
    restaurants = {r.id: r for r in db.query(Restaurant).all()}
    return templates.TemplateResponse(
        "dashboard/rider.html",
        {
            "request": request,
            "user": current_user,
            "available_orders": available,
            "my_orders": my_orders,
            "restaurants": restaurants,
            "STATUS_LABEL": STATUS_LABEL,
            "OrderStatus": OrderStatus,
        },
    )
