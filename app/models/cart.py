from sqlalchemy import Column, Integer, ForeignKey
from ..database import Base
from sqlalchemy.orm import relationship

class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    product = relationship("Product")
    user = relationship("User", back_populates="carts")