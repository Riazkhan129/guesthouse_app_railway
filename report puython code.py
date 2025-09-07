from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sample data (replace with DB queries)
GUESTS_DB = [
    {
        "nic_passport_number": "12345",
        "name": "Ali Khan",
        "contact_number": "03001234567",
        "email": "ali@example.com",
        "address": "Karachi, Pakistan",
        "nationality": "Pakistani",
        "emergency_contact": "03111234567"
    },
    {
        "nic_passport_number": "67890",
        "name": "Sara Ahmed",
        "contact_number": "03007654321",
        "email": "sara@example.com",
        "address": "Lahore, Pakistan",
        "nationality": "Pakistani",
        "emergency_contact": "03211234567"
    }
]

BOOKINGS_DB = [
    {
        "nic_passport_number": "12345",
        "guest_name": "Ali Khan",
        "actual_checkin_time": "2025-08-01 14:00",
        "actual_checkout_date": "2025-08-05 12:00",
        "room_number": "101"
    },
    {
        "nic_passport_number": "12345",
        "guest_name": "Ali Khan",
        "actual_checkin_time": "2025-07-10 13:00",
        "actual_checkout_date": "2025-07-12 11:00",
        "room_number": "102"
    },
    {
        "nic_passport_number": "67890",
        "guest_name": "Sara Ahmed",
        "actual_checkin_time": "2025-08-03 15:00",
        "actual_checkout_date": "2025-08-06 11:00",
        "room_number": "201"
    }
]

# Pydantic models
class Guest(BaseModel):
    nic_passport_number: str
    name: str
    contact_number: str
    email: str
    address: str
    nationality: str
    emergency_contact: str

class Booking(BaseModel):
    nic_passport_number: str
    guest_name: str
    actual_checkin_time: str
    actual_checkout_date: str
    room_number: str

# Endpoint: dropdown list of guests with check-in
@app.get("/bookings/checked_in", response_model=List[Booking])
def get_checked_in_guests():
    return [b for b in BOOKINGS_DB if b["actual_checkin_time"]]

# Endpoint: guest details by NIC
@app.get("/guests/{nic}", response_model=Guest)
def get_guest_by_nic(nic: str):
    guest = next((g for g in GUESTS_DB if g["nic_passport_number"] == nic), None)
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest

# Endpoint: all bookings for a guest
@app.get("/bookings/by_nic/{nic}", response_model=List[Booking])
def get_bookings_by_nic(nic: str):
    return [b for b in BOOKINGS_DB if b["nic_passport_number"] == nic]
