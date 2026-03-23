from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from app.routers import products # Thêm dòng này
router = APIRouter(
    prefix="/products",
    tags=["Quản lý Sản phẩm"]
)

# 1. XEM TẤT CẢ (Có phân trang)
@router.get("/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 50, db: Session = Depends(database.get_db)):
    return db.query(models.Product).offset(skip).limit(limit).all()

# 2. XEM CHI TIẾT 1 SẢN PHẨM
@router.get("/{product_id}", response_model=schemas.Product)
def read_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm")
    return db_product

# 3. THÊM MỚI
@router.post("/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# 4. CẬP NHẬT (Sửa)
@router.put("/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Sản phẩm không tồn tại để sửa")
    
    # Cập nhật từng trường dữ liệu
    for key, value in product.model_dump().items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product

# 5. XÓA
@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Không thấy sản phẩm để xóa")
    
    db.delete(db_product)
    db.commit()
    return {"message": f"Đã xóa thành công sản phẩm ID {product_id}"}