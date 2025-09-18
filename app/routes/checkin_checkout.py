# app/routes/checkin_checkout.py

from fastapi import APIRouter, Depends, HTTPException, Request
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

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

# Check-in endpoint

#----------------
from ..models import CheckinData

@router.put("/checkin/{booking_id}")
def checkin_guest(request: Request, booking_id: int, data: CheckinData):
    client_id = get_client_id(request)
    success = crud.checkin_booking(client_id, booking_id, data)
    if success:
        return {"message": "Guest checked in successfully"}
    
    raise HTTPException(status_code=400, detail="Check-in failed")




# Check-out endpoint
@router.get("/checkedin")
def get_checkedin_bookings(request: Request):
    client_id = get_client_id(request)
    bookings = crud.get_checkedin_bookings(client_id)
    return bookings

@router.post("/checkout/{booking_id}")
def check_out(request: Request, booking_id: int, db = Depends(get_db), user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    booking = crud.get_booking(client_id, db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if not booking.actual_checkin_time:
        raise HTTPException(status_code=400, detail="Cannot check out before check-in")

    if booking.actual_checkout_time:
        raise HTTPException(status_code=400, detail="Guest already checked out")

    now = datetime.now()
    crud.update_checkout_time(client_id, db, booking_id, now)

    return {"status": "success", "message": f"Checked out at {now}"}

# ----------- Fetch Price for Checkout -----
@router.get("/{room_number}")
def read_room(request: Request, room_number: str):
    client_id = get_client_id(request)
    room = crud.get_room_by_number(client_id, room_number)
    if room:
        return room
    raise HTTPException(status_code=404, detail="Room not found")

@router.get("/guest_name/{nic}")
def get_guest_name_by_nic(request: Request, nic: str):
    client_id = get_client_id(request)
    print("IN CHECKIN_CHECKOUT NIC =", nic)
    guest_name = crud.get_guest_name_by_nic(client_id, nic)
    if guest_name:
        return guest_name  # returns actual name dictionary from crud
    raise HTTPException(status_code=404, detail="Guest not found")
