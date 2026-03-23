from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
<<<<<<< HEAD

# Quan trọng: Phải import cái file router vào thì Python mới hiểu "products" là gì
from app.routers import products 
from app.database import engine, get_db, Base
from app import models, schemas

# Tạo bảng tự động trong SQLite
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Website Bán Sản Phẩm Thú Cưng - Nhóm 14")

# Kết nối Router từ file products.py
app.include_router(products.router)
=======
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .database import SessionLocal, engine, get_db
from . import models, schemas
from .routers import auth

# Lệnh này sẽ tự động tạo file pet_shop.db và các bảng (products, users...) 
# nếu chúng chưa tồn tại
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Website Bán Sản Phẩm Thú Cưng - Nhóm 14")

# Cấu hình Rate Limiting
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Đăng ký các router
app.include_router(auth.router)
>>>>>>> 5d7198a0547d63d0a5fb9b3e73db4afdff710709

@app.get("/")
def home():
    return {"message": "Chào mừng đến với Pet Shop API!"}

# --- PHẦN QUẢN LÝ USER ---
@app.post("/users/", response_model=schemas.UserResponse, tags=["Quản lý User"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(username=user.username, password=user.password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- PHẦN GIỎ HÀNG ---
@app.post("/cart/", response_model=schemas.CartResponse, tags=["Giỏ hàng"])
def add_to_cart(cart: schemas.CartCreate, db: Session = Depends(get_db)):
    # Tạm thời fix cứng user_id = 1 để test database
    db_cart = models.Cart(user_id=1, product_id=cart.product_id, quantity=cart.quantity)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart