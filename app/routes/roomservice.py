from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
from ..auth import get_current_user
from .. import crud
from typing import List


router = APIRouter(
    prefix="/roomservice",
    tags=["Roomservice"]
)



# 📦 Pydantic Model
class RoomServiceRequestIn(BaseModel):
    room_id: int
    nic_passport_number: str
    category_id: int
    expense_item_id: int
    quantity: int
    unit_price: int
    notes: str = ""
    booking_id: int
    status: str

# ✅ Pydantic model for status update
class RoomServiceStatusUpdate(BaseModel):
    status: str

class RoomServiceSummaryOut(BaseModel):
    category_name: str
    total_amount: int

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id



@router.get("/checkedin")
def fetch_checkedin_bookings_with_guest(request: Request):
    client_id = get_client_id(request)
    print("In rromservice / checkedin ")
    return crud.get_checkedin_bookings_with_guest(client_id)

@router.get("/open")
def get_open_roomservice_requests(request: Request):
    client_id = get_client_id(request)
    return crud.get_open_roomservice_requests(client_id)

@router.put("/update/{service_id}")
def update_room_service_status(service_id: int, data: RoomServiceStatusUpdate, request: Request):
    client_id = get_client_id(request)
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    
    updated = crud.update_room_service_status(client_id, service_id, data.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Room service record not found or update failed")
    return {"message": "✅ Status updated successfully"}

# 🛎️ Create Room Service Entry
@router.post("/create")
def create_room_service(data: RoomServiceRequestIn, request: Request):
    client_id = get_client_id(request)
   # crud.create_room_service_request
    return crud.create_room_service_request(client_id, data)

@router.get("/summary/by_booking/{booking_id}")
def get_roomservice_summary(booking_id: int, request: Request):
    client_id = get_client_id(request)
    return crud.get_roomservice_summary_by_booking(client_id, booking_id)

# 📊 Summary by Category
#@router.get("/summary/by_booking/{bookingId}")
#def get_roomservice_summary(booking_id: int, request: Request):
#    client_id = get_client_id(request)
#    print("IN ROOMSERVICE /summary/by_booking/bookingid")
    # summary = crud.get_roomservice_summary_by_booking
    # return summary
#    return crud.get_roomservice_summary_by_booking(client_id, booking_id)


@router.get("/items/by_booking/{booking_id}")
def get_roomservice_items(booking_id: int, request: Request):
    client_id = get_client_id(request)
    #items = crud.get_roomservice_items_by_booking
    # return items
    return crud.get_roomservice_items_by_booking(client_id, booking_id)
