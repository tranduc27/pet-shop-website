from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, get_db
from . import models, schemas

# Lệnh này sẽ tự động tạo file pet_shop.db và các bảng (products,...) 
# nếu chúng chưa tồn tại
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Website Bán Sản Phẩm Thú Cưng - Nhóm 14")

@app.get("/")
def home():
    return {"message": "Chào mừng đến với Pet Shop API!"}

# Endpoint để lấy danh sách sản phẩm (Dùng cho trang chủ website)
@app.get("/products/", response_model=list[schemas.Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

# Endpoint để thêm một sản phẩm mới (Dùng cho trang Admin)
@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product