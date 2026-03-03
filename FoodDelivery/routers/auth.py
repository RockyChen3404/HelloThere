from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
from models.user import User, UserRole
from schemas.user import UserRegister, UserLogin, UserOut, TokenOut
from core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    from core.security import decode_token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    from core.security import decode_token
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        return None
    return db.query(User).filter(User.id == payload.get("sub")).first()


@router.post("/register", response_model=TokenOut)
def register(data: UserRegister, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="手机号已注册")
    user = User(
        name=data.name,
        phone=data.phone,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
        address=data.address,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": user.id, "role": user.role})
    response.set_cookie("access_token", token, httponly=True, max_age=86400)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    token = create_access_token({"sub": user.id, "role": user.role})
    response.set_cookie("access_token", token, httponly=True, max_age=86400)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "已登出"}
