from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests

BOT_TOKEN = "8448838195:AAE8LjwIESPPBJOH0NTiz3Yo4bhktZZlss0"
CHAT_ID = "918858687"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Товары ---
products = []
for i in range(1, 101):
    products.append({
        "id": i,
        "name": f"Импортная сладость №{i}",
        "price": 100 + i
    })

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
    text = f"🛒 Новый заказ №{order_counter}\n\n"

    if order.username:
        text += f"👤 @{order.username}\n"
    if order.user_id:
        text += f"ID: {order.user_id}\n"

    text += "\nТовары:\n"

    for item in order.items:
        product = next((p for p in products if p["id"] == item.id), None)
        if product:
            total += product["price"] * item.quantity
            text += f"- {product['name']} x{item.quantity}\n"

    text += f"\n💰 Сумма: {total} ₽"

    # --- отправка в Telegram ---
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text
        }
    )

    new_order = {
        "order_id": order_counter,
        "total_price": total
    }

    orders.append(new_order)
    order_counter += 1

    return new_order
