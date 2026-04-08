import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import engine, Base
from app.models import Review, Product, User, Cart, Order, OrderItem, Wishlist

print("Attempting to create all missing tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
