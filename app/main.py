from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import products, auth, cart # Import thêm cart

# Khởi tạo DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet Shop API - Nhóm 14")

# Cấu hình bảo mật
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ĐĂNG KÝ TẤT CẢ ROUTERS Ở ĐÂY
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router) # Đã tách xong!

@app.get("/")
def home():
    return {"message": "Hệ thống Pet Shop đã sẵn sàng!"}