import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from database import Base, engine
import models  # ensure all models are registered

from routers import auth, restaurants, menu, cart, orders, reviews, pages

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FoodDelivery - 美团外卖系统", version="1.0.0")

# Routers
app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(pages.router)  # HTML pages (last, catches "/")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
