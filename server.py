from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# --- CORS (обязательно для Vercel) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Товары ---
products = []

# создаём 100 товаров
for i in range(1, 101):
    products.append({
        "id": i,
        "name": f"Импортная сладость №{i}",
        "price": 100 + i
    })

# --- Заказы ---
orders = []
order_counter = 1


class OrderItem(BaseModel):
    id: int
    quantity: int


class Order(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    items: List[OrderItem]


@app.get("/")
def root():
    return {"status": "Candy shop API is running 🍬"}


@app.get("/products")
def get_products():
    return products


@app.post("/create-order")
def create_order(order: Order):
    global order_counter

    total = 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.id), None)
        if product:
            total += product["price"] * item.quantity

    new_order = {
        "order_id": order_counter,
        "user_id": order.user_id,
        "username": order.username,
        "items": order.items,
        "total_price": total
    }

    orders.append(new_order)
    order_counter += 1

    return {
        "order_id": new_order["order_id"],
        "total_price": new_order["total_price"]
    }
