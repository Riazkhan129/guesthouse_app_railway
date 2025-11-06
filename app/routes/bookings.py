from fastapi import APIRouter, Depends, HTTPException, Query, Request
# from ..db import get_db
# from ..db import get_client_id
from ..auth import get_current_user
from .. import crud
from ..models import BookingCreate, BookingOut, BookingResponse, CancelBookingRequest, BookingOutCheckIn
import sqlite3

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

# app/booking.py

@router.get("/total")
def get_room_summary(request: Request, checkin_date: str = Query(...)):
    client_id = get_client_id(request)
    print("IN BOOKINGS CHECKIN_DATE = ", checkin_date)
    summary = crud.get_room_stats(client_id, checkin_date)
    return summary

@router.post("/", response_model=BookingResponse)
def create_booking(request: Request, data: BookingCreate):
    client_id = get_client_id(request)
    print("In bookings Before crud.create_booking")
    booking_id = crud.create_booking(client_id, data.dict())
    if not booking_id:
        print("Booking ID is None! Something went wrong during insert.")
    else:
        print("Booking ID created:", booking_id)
    return {"booking_id": booking_id} 

@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking_by_id(request: Request, booking_id: int):
    client_id = get_client_id(request)
    booking = crud.get_booking(client_id, booking_id)
    if booking:
        return booking
    raise HTTPException(status_code=404, detail="Booking not found")

# ------- Get all bookings ------------
@router.get("/", response_model=list[BookingOut])
def get_all_bookings(request: Request,):
    client_id = get_client_id(request)
    return crud.get_all_bookings(client_id)

#------- Get Bookings by NIC for Guest Report -------------
@router.get("/by_nic/{selected_nic}", response_model=list[BookingOut])
def get_bookings_by_nic(request: Request, selected_nic: str):
    client_id = get_client_id(request)
    bookings = crud.get_bookings_by_nic(client_id, selected_nic)
    print("IN BOOKING -> BOOKINGS = ", bookings)
    if bookings:
        return bookings
    raise HTTPException(status_code=404, detail="No bookings found for this NIC")

# ------- Get todays bookings ------------
@router.get("/today", response_model=list[BookingOutCheckIn])
def get_today_bookings(request: Request,):
    client_id = get_client_id(request)
    print("In bookings Before crud.get_today_bookings()")
    return crud.get_today_bookings(client_id)

@router.put("/bookings/update/{booking_id}")
def update_booking_by_id(request: Request, booking_id: int, data: dict):
    client_id = get_client_id(request)
    booking = crud.get_booking(client_id, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    crud.update_booking(client_id, booking_id, data)
    return {"message": "Booking updated successfully"}

@router.put("/cancel/{booking_id}")
def cancel_booking_by_id(request: Request, booking_id: int, data: CancelBookingRequest):
    client_id = get_client_id(request)
    room_number = data.room_number
    success = crud.cancel_booking(client_id, booking_id, room_number)
    if success:
        return {"message": "Booking cancelled successfully"}
    raise HTTPException(status_code=400, detail="Unable to cancel booking")

@router.get("/upcoming")
def get_upcoming(request: Request,):
    client_id = get_client_id(request)
    print("IN GET_UPCOMING BEFORE CRUD")
    return crud.get_upcoming_bookings(client_id)
    print("AFTER GET_UPCOMING BEFORE CRUD")
    


