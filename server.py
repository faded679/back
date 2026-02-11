from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import requests
import json
from fastapi.middleware.cors import CORSMiddleware


BOT_TOKEN = "8448838195:AAE8LjwIESPPBJOH0NTiz3Yo4bhktZZlss0"
ADMIN_ID = 918858687  # сюда вставь свой Telegram ID

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для теста разрешаем всё
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


engine = create_engine("sqlite:///shop.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()


# =======================
# МОДЕЛИ
# =======================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)


class OrderDB(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    items = Column(String)  # храним JSON строкой
    total = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)


# =======================
# ЗАПОЛНЯЕМ ТОВАРЫ
# =======================

def seed_products():
    session = Session()

    if session.query(Product).count() == 0:

        sweets = [
            ("KitKat Japan Matcha", 350),
            ("KitKat Sakura", 370),
            ("Reese's Peanut Butter Cups", 250),
            ("Twizzlers Strawberry", 280),
            ("Haribo Goldbears USA", 200),
            ("Skittles Sour USA", 220),
            ("Takis Fuego", 390),
            ("Pocky Chocolate", 180),
            ("Pocky Strawberry", 190),
            ("Snickers Almond USA", 210),
        ]

        for name, price in sweets:
            session.add(Product(name=name, price=price))

        # добавим ещё 100 тестовых
        for i in range(1, 101):
            session.add(Product(
                name=f"Импортная сладость №{i}",
                price=100 + i
            ))

        session.commit()

    session.close()


seed_products()


# =======================
# API
# =======================

@app.get("/products")
def get_products():
    session = Session()
    products = session.query(Product).all()
    session.close()

    return [
        {"id": p.id, "name": p.name, "price": p.price}
        for p in products
    ]


class Order(BaseModel):
    items: list
    total: float


@app.post("/order")
def create_order(order: Order):

    session = Session()

    # сохраняем в БД
    db_order = OrderDB(
        items=json.dumps(order.items, ensure_ascii=False),
        total=order.total
    )

    session.add(db_order)
    session.commit()
    session.close()

    # отправляем уведомление в Telegram
    text = f"🛒 Новый заказ!\n\nСумма: {order.total} ₽\n\n"

    for item in order.items:
        text += f"- {item['name']} × {item['qty']} ({item['price']} ₽)\n"

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={
            "chat_id": ADMIN_ID,
            "text": text
        }
    )

    return {"status": "ok"}


# посмотреть все заказы (для проверки)
@app.get("/orders")
def get_orders():
    session = Session()
    orders = session.query(OrderDB).all()
    session.close()

    return [
        {
            "id": o.id,
            "items": o.items,
            "total": o.total,
            "created_at": o.created_at
        }
        for o in orders
    ]
