from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# --- Đã cập nhật đường dẫn import theo cấu trúc thư mục mới ---
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- CẤU HÌNH BẢO MẬT & TOKEN ---
SECRET_KEY = "khoa-bao-mat-sieu-cap-cua-nhom-ban" # Thực tế nên để trong file .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Schema cho Token (Tạo tại đây để trả về cho User)
class Token(BaseModel):
    access_token: str
    token_type: str

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- API ĐĂNG KÝ ---
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Quét DB bằng 'username' thay vì 'email'
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username này đã tồn tại.")

    # 2. Băm mật khẩu
    hashed_pwd = get_password_hash(user.password)
    
    # 3. Lưu vào DB (Đạt để tên cột là 'password' nên ta lưu mật khẩu đã băm vào đây)
    new_user = User(
        username=user.username, 
        password=hashed_pwd, 
        role=user.role # Sẽ tự lấy default là "Customer" như trong schema của Đạt
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- API ĐĂNG NHẬP ---
@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. Tìm user bằng username
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # 2. So sánh mật khẩu
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai username hoặc mật khẩu.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Tạo token (Nhét thêm role vào token để tiện phân quyền sau này)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}