from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(
    prefix="/orders",
    tags=["Đơn hàng"]
)

@router.post("/checkout", response_model=schemas.OrderResponse)
def checkout(db: Session = Depends(database.get_db)):
    # Tạm thời fix cứng user_id = 1 (Giống với cart.py)
    user_id = 1
    
    # 1. Lấy giỏ hàng
    cart_items = db.query(models.Cart).filter(models.Cart.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Giỏ hàng trống")
    
    # 2. Tính tiền và kiểm tra tồn kho
    total_price = 0
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Sản phẩm ID {item.product_id} không tồn tại")
        
        # Check stock (xử lý None fallback về 0)
        current_stock = product.stock if product.stock is not None else 0
        if current_stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Sản phẩm '{product.name}' không đủ số lượng (chỉ còn {current_stock})")
        
        # Trừ kho
        product.stock = current_stock - item.quantity
        total_price += product.price * item.quantity

    # 3. Tạo Đơn hàng (Order)
    new_order = models.Order(user_id=user_id, total_price=total_price, status="completed")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # 4. Tạo chi tiết đơn (OrderItem)
    for item in cart_items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        order_item = models.OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=product.price
        )
        db.add(order_item)
    
    # 5. Dọn sạch Giỏ hàng
    db.query(models.Cart).filter(models.Cart.user_id == user_id).delete()
    db.commit()
    
    db.refresh(new_order)
    return new_order
