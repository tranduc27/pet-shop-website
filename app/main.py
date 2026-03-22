from fastapi import FastAPI
from .database import engine, Base
from .routers import products # Giả sử bạn sẽ tạo router này

# Tạo các bảng trong Database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount các thư mục static để hiện ảnh sản phẩm
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def root():
    return {"message": "API Website Bán Sản Phẩm Thú Cưng - Nhóm 14"}
