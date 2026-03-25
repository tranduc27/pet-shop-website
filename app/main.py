from fastapi import FastAPI, Request                          # thêm Request
from fastapi.staticfiles import StaticFiles                   # thêm
from fastapi.templating import Jinja2Templates                # thêm
from fastapi.middleware.cors import CORSMiddleware            # thêm
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routers import products, auth, cart, orders, services

# Khởi tạo DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pet Shop API - Nhóm 14")

# Cấu hình bảo mật
app.state.limiter = auth.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS - cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files và Templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ĐĂNG KÝ TẤT CẢ ROUTERS Ở ĐÂY
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(services.router)

# Trả về giao diện HTML thay vì JSON
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/shop")
def shop(request: Request):
    return templates.TemplateResponse("shop.html", {"request": request})

@app.get("/services")
def services_page(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})