from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Appointment(Base):
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    date_time = Column(String)
    notes = Column(String, nullable=True)
    status = Column(String, default="pending")
    
    user = relationship("User")
    service = relationship("Service")
