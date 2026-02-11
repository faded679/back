from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base
import json

# -----------------------------
# БАЗА ДАННЫХ
# -----------------------------

DATABASE_URL = "sqlite:///./shop.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

Session = sessionmaker(bind=engine)
Base = declarative_base()


# -----------------------------
# МОДЕЛИ
# -----------------------------

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    username = Column(String)
    items = Column(Text)  # JSON строка
    total_price = Column(Float)


Base.metadata.create_all(bind=engine)


# -----------------------------
# FASTAPI
# -----------------------------

app = FastAPI()

# CORS (чтобы Mini App работал)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# СИДИРОВАНИЕ ТОВАРОВ
# -----------------------------

def seed_products():
    db = Session()
    if db.query(Product).count() == 0:
        products = [
            Product(name="KitKat Japan Matcha", price=350),
            Product(name="KitKat Sakura", price=370),
            Product(name="Reese's Peanut Butter Cups", price=250),
            Product(name="Twizzlers Strawberry", price=280),
            Product(name="Haribo Goldbears USA", price=200),
            Product(name="Skittles Sour USA", price=220),
            Product(name="Takis Fuego", price=390),
            Product(name="Pocky Chocolate", price=180),
            Product(name="Pocky Strawberry", price=190),
            Product(name="Snickers Almond USA", price=210),
        ]

        # добавим ещё 100 тестовых
        for i in range(1, 101):
            products.append(
                Product(name=f"Импортная сладость №{i}", price=100 + i)
            )

        db.add_all(products)
        db.commit()
    db.close()


seed_products()


# -----------------------------
# ЭНДПОИНТЫ
# -----------------------------

@app.get("/products")
def get_products():
    db = Session()
    products = db.query(Product).all()
    db.close()
    return products


@app.post("/create-order")
def create_order(data: dict = Body(...)):
    db = Session()

    items = data.get("items", [])
    user_id = data.get("user_id")
    username = data.get("username")

    total = 0

    for item in items:
        product = db.query(Product).filter(Product.id == item["id"]).first()
        if product:
            total += product.price * item["quantity"]

    order = Order(
        user_id=user_id,
        username=username,
        items=json.dumps(items),
        total_price=total
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    db.close()

    return {
        "order_id": order.id,
        "total_price": total
    }
