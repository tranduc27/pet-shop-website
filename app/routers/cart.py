from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(
    prefix="/cart",
    tags=["Giỏ hàng"]
)

@router.post("/", response_model=schemas.CartResponse)
def add_to_cart(cart: schemas.CartCreate, db: Session = Depends(database.get_db)):
    # Tạm thời fix cứng user_id = 1, sau này sẽ lấy từ Token
    db_cart = models.Cart(user_id=1, product_id=cart.product_id, quantity=cart.quantity)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart