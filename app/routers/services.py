from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database

router = APIRouter(prefix="/services", tags=["Services"])

@router.on_event("startup")
def seed_services():
    db = database.SessionLocal()
    try:
        count = db.query(models.Service).count()
        if count == 0:
            s1 = models.Service(
                name="Pet Spa & Grooming",
                description="Cắt tỉa lông chuyên nghiệp, tắm massage thảo dược giúp các bé thơm tho, sạch sẽ và ngăn ngừa ve rận.",
                icon="fa-scissors"
            )
            s2 = models.Service(
                name="Khách Sạn Pet Hotel",
                description="Khu vực lưu chuồng rộng rãi, trang bị điều hòa và camera 24/7. Các bé được vui chơi chạy nhảy mỗi ngày.",
                icon="fa-house-medical"
            )
            db.add(s1)
            db.add(s2)
            db.commit()
    except Exception as e:
        print("Seed errors: ", e)
    finally:
        db.close()

# API
@router.get("/api/services", response_model=List[schemas.ServiceItem])
def list_services(db: Session = Depends(database.get_db)):
    return db.query(models.Service).all()

@router.post("/api/appointments")
def book_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(database.get_db)):
    # Create an appointment in database. Defaults user_id to 1.
    db_app = models.Appointment(
        user_id=1,
        service_id=appointment.service_id,
        date_time=appointment.date_time,
        notes=appointment.notes,
        status="pending"
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return {"message": "Đặt lịch thành công!", "id": db_app.id}

