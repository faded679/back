from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

app = FastAPI()

# -----------------------------
# CORS (ОБЯЗАТЕЛЬНО для Vercel)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # позже можно заменить на домен Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Товары магазина
# -----------------------------
products = [
    {"id": 1, "name": "KitKat Japan Matcha", "price": 350},
    {"id": 2, "name": "KitKat Sakura", "price": 370},
    {"id": 3, "name": "Reese's Peanut Butter Cups", "price": 250},
    {"id": 4, "name": "Twizzlers Strawberry", "price": 280},
    {"id": 5, "name": "Haribo Goldbears USA", "price": 200},
    {"id": 6, "name": "Skittles Sour USA", "price": 220},
    {"id": 7, "name": "Takis Fuego", "price": 390},
    {"id": 8, "name": "Pocky Chocolate", "price": 180},
    {"id": 9, "name": "Pocky Strawberry", "price": 190},
    {"id": 10, "name": "Snickers Almond USA", "price": 210},
]

# -----------------------------
# Модель заказа
# -----------------------------
class CartItem(BaseModel):
    id: int
    name: str
    price: float
    quantity: int


class Order(BaseModel):
    items: List[CartItem]
    total: float


# -----------------------------
# Хранилище заказов (временно)
# -----------------------------
orders = []

# -----------------------------
# Роуты
# -----------------------------

@app.get("/")
def root():
    return {"status": "Candy Shop API is running 🍬"}


@app.get("/products")
def get_products():
    return products


@app.post("/order")
def create_order(order: Order):
    order_id = str(uuid.uuid4())[:8]

    new_order = {
        "order_id": order_id,
        "items": order.items,
        "total": order.total,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    orders.append(new_order)

    return {
        "success": True,
        "order_id": order_id,
        "total": order.total
    }


@app.get("/orders")
def get_orders():
    return orders
