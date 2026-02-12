import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

# =============================
# DATABASE
# =============================

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# =============================
# MODELS
# =============================

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    image = Column(String)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Float)


# =============================
# APP
# =============================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================
# CREATE TABLES
# =============================

Base.metadata.create_all(bind=engine)


# =============================
# SEED PRODUCTS (если пусто)
# =============================

def seed_products():
    db = SessionLocal()

    if db.query(Product).count() == 0:
        products = [
            Product(name="KitKat Japan", price=350, image="https://via.placeholder.com/150"),
            Product(name="Snickers USA", price=180, image="https://via.placeholder.com/150"),
            Product(name="Milka Oreo Germany", price=220, image="https://via.placeholder.com/150"),
            Product(name="Twix UK", price=190, image="https://via.placeholder.com/150"),
            Product(name="Pocky Strawberry", price=270, image="https://via.placeholder.com/150"),
        ]

        db.add_all(products)
        db.commit()

    db.close()


seed_products()


# =============================
# ROUTES
# =============================

@app.get("/")
def root():
    return {"status": "API with PostgreSQL running 🍬"}


@app.get("/products")
def get_products():
    db = SessionLocal()
    products = db.query(Product).all()

    result = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "image": p.image
        }
        for p in products
    ]

    db.close()
    return result


@app.post("/create-order")
def create_order(data: dict):
    db = SessionLocal()

    new_order = Order(total=data["total"])
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    db.close()

    return {"message": f"Заказ №{new_order.id} оформлен ✅"}


@app.get("/orders")
def get_orders():
    db = SessionLocal()

    orders = db.query(Order).all()
    result = [
        {"id": o.id, "total": o.total}
        for o in orders
    ]

    db.close()
    return result
