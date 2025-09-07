# app/routes/checkin_checkout.py

from fastapi import APIRouter, Depends, HTTPException
#from sqlalchemy.orm import Session
from datetime import datetime
from ..db import get_db
from ..auth import get_current_user
from .. import crud
from pydantic import BaseModel
from ..models import CheckinData

router = APIRouter(
    prefix="/checkin_checkout",
    tags=["Check-In/Check-Out"]
)

# Check-in endpoint

#----------------
from ..models import CheckinData

@router.put("/checkin/{booking_id}")
def checkin_guest(booking_id: int, data: CheckinData):
    
    # Pass the individual fields from the model
    success = crud.checkin_booking(booking_id, data)
    if success:
        return {"message": "Guest checked in successfully"}
    
    raise HTTPException(status_code=400, detail="Check-in failed")




# Check-out endpoint
@router.get("/checkedin")
def get_checkedin_bookings():
    bookings = crud.get_checkedin_bookings()
    return bookings

@router.post("/checkout/{booking_id}")
def check_out(booking_id: int, db = Depends(get_db), user: str = Depends(get_current_user)):
    booking = crud.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if not booking.actual_checkin_time:
        raise HTTPException(status_code=400, detail="Cannot check out before check-in")

    if booking.actual_checkout_time:
        raise HTTPException(status_code=400, detail="Guest already checked out")

    now = datetime.now()
    crud.update_checkout_time(db, booking_id, now)

    return {"status": "success", "message": f"Checked out at {now}"}

# ----------- Fetch Price for Checkout -----

#router = APIRouter()

@router.get("/{room_number}")
def read_room(room_number: str):
    room = crud.get_room_by_number(room_number)
    if room:
        return room
    raise HTTPException(status_code=404, detail="Room not found")

@router.get("/guest_name/{nic}")
def get_guest_name_by_nic(nic: str):
    print("IN CHECKIN_CHECKOUT NIC =", nic)
    guest_name = crud.get_guest_name_by_nic(nic)
    if guest_name:
        return guest_name  # returns actual name dictionary from crud
    raise HTTPException(status_code=404, detail="Guest not found")
