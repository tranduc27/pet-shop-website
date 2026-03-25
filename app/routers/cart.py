from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

from typing import List

router = APIRouter(
    prefix="/cart",
    tags=["Giỏ hàng"]
)

@router.get("/", response_model=List[schemas.CartResponse])
def get_cart(db: Session = Depends(database.get_db)):
    # Tạm thời fix cứng user_id = 1, sau này sẽ lấy từ Token
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == 1).all()
    return cart_items

@router.post("/", response_model=schemas.CartResponse)
def add_to_cart(cart: schemas.CartCreate, db: Session = Depends(database.get_db)):
    # Tạm thời fix cứng user_id = 1, sau này sẽ lấy từ Token
    
    # Kiểm tra xem sản phẩm đã có trong giỏ chưa
    existing_item = db.query(models.Cart).filter(
        models.Cart.user_id == 1, 
        models.Cart.product_id == cart.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += cart.quantity
        db.commit()
        db.refresh(existing_item)
        return existing_item
        
    db_cart = models.Cart(user_id=1, product_id=cart.product_id, quantity=cart.quantity)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

@router.delete("/{cart_id}")
def remove_from_cart(cart_id: int, db: Session = Depends(database.get_db)):
    db_cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not db_cart:
        raise HTTPException(status_code=404, detail="Không tìm thấy sản phẩm trong giỏ")
    
    db.delete(db_cart)
    db.commit()
    return {"message": "Đã xóa khỏi giỏ hàng"}