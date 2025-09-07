from fastapi import APIRouter, Depends, HTTPException, Query
from ..db import get_db
from ..auth import get_current_user
from .. import crud
from ..models import BookingCreate, BookingOut, BookingResponse, CancelBookingRequest, BookingOutCheckIn
import sqlite3

router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)

# app/booking.py

@router.get("/total")
def get_room_summary(checkin_date: str = Query(...)):
    print("IN BOOKINGS CHECKIN_DATE = ", checkin_date)
    summary = crud.get_room_stats(checkin_date)
    return summary

@router.post("/", response_model=BookingResponse)
def create_booking(data: BookingCreate):
    print("In bookings Before crud.create_booking")
    booking_id = crud.create_booking(data.dict())
    if not booking_id:
        print("Booking ID is None! Something went wrong during insert.")
    else:
        print("Booking ID created:", booking_id)
    return {"booking_id": booking_id} 

@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking_by_id(booking_id: int):
    booking = crud.get_booking(booking_id)
    if booking:
        return booking
    raise HTTPException(status_code=404, detail="Booking not found")

# ------- Get all bookings ------------
@router.get("/", response_model=list[BookingOut])
def get_all_bookings():
    return crud.get_all_bookings()

#------- Get Bookings by NIC for Guest Report -------------
@router.get("/by_nic/{selected_nic}", response_model=list[BookingOut])
def get_bookings_by_nic(selected_nic: str):
    bookings = crud.get_bookings_by_nic(selected_nic)
    print("IN BOOKING -> BOOKINGS = ", bookings)
    if bookings:
        return bookings
    raise HTTPException(status_code=404, detail="No bookings found for this NIC")



# ------- Get todays bookings ------------
@router.get("/today", response_model=list[BookingOutCheckIn])
def get_today_bookings():
    print("In bookings Before crud.get_today_bookings()")
    return crud.get_today_bookings()

@router.put("/bookings/update/{booking_id}")
def update_booking_by_id(booking_id: int, data: dict):
    booking = crud.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    crud.update_booking(booking_id, data)
    return {"message": "Booking updated successfully"}

@router.put("/cancel/{booking_id}")
def cancel_booking_by_id(booking_id: int, data: CancelBookingRequest):
    room_number = data.room_number
    success = crud.cancel_booking(booking_id, room_number)
    if success:
        return {"message": "Booking cancelled successfully"}
    raise HTTPException(status_code=400, detail="Unable to cancel booking")

@router.get("/upcoming")
def get_upcoming():
    return crud.get_upcoming_bookings()

#from fastapi import Query

    success = crud.checkout_booking(booking_id, final_payment)
    if success:
        return {"message": "Guest checked out successfully"}
    raise HTTPException(status_code=400, detail="Check-out failed")


