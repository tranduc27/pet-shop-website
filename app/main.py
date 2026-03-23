from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, get_db, Base
from app import models, schemas   # chỉ import 1 lần

# Tạo bảng
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Website Bán Sản Phẩm Thú Cưng - Nhóm 14")


@app.get("/")
def home():
    return {"message": "Chào mừng đến với Pet Shop API!"}


@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()


@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product