from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db, engine, Base, Availability, Reservation
from schemas import (
    AvailabilityCreate, AvailabilityResponse, AvailabilityBulkUpdate,
    ReservationCreate, ReservationResponse, ErrorResponse
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Doctor Reservation Service", version="1.0.0")

@app.get("/availability", response_model=List[AvailabilityResponse])
def get_availability(db: Session = Depends(get_db)):
    return db.query(Availability).all()

@app.post("/availability", response_model=AvailabilityResponse)
def create_availability(
    availability: AvailabilityCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(Availability).filter(
        Availability.day_of_week == availability.day_of_week,
        Availability.hour == availability.hour
    ).first()
    
    if existing:
        existing.is_available = availability.is_available
        db.commit()
        db.refresh(existing)
        return existing
    
    db_availability = Availability(**availability.dict())
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

@app.put("/availability/bulk", response_model=List[AvailabilityResponse])
def bulk_update_availability(
    bulk_data: AvailabilityBulkUpdate,
    db: Session = Depends(get_db)
):
    updated_availabilities = []
    
    for availability_data in bulk_data.availabilities:
        existing = db.query(Availability).filter(
            Availability.day_of_week == availability_data.day_of_week,
            Availability.hour == availability_data.hour
        ).first()
        
        if existing:
            existing.is_available = availability_data.is_available
        else:
            existing = Availability(**availability_data.dict())
            db.add(existing)
        
        updated_availabilities.append(existing)
    
    db.commit()
    for availability in updated_availabilities:
        db.refresh(availability)
    
    return updated_availabilities

@app.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db)
):
    availability = db.query(Availability).filter(
        Availability.day_of_week == reservation.day_of_week,
        Availability.hour == reservation.hour,
        Availability.is_available == True
    ).first()
    
    if not availability:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Time slot not available: Day {reservation.day_of_week}, Hour {reservation.hour}"
        )
    
    existing_reservation = db.query(Reservation).filter(
        Reservation.day_of_week == reservation.day_of_week,
        Reservation.hour == reservation.hour,
        Reservation.reservation_date == reservation.reservation_date
    ).first()
    
    if existing_reservation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot already reserved for {reservation.reservation_date.strftime('%Y-%m-%d')}"
        )
    
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    
    return db_reservation

@app.get("/reservations", response_model=List[ReservationResponse])
def get_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).order_by(Reservation.reservation_date, Reservation.hour).all()

@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )
    
    db.delete(reservation)
    db.commit()
    return {"message": "Reservation cancelled successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
