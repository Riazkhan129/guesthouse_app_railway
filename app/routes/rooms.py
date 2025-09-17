from fastapi import APIRouter, Depends, HTTPException, Request
# from sqlalchemy.orm import Session
from ..db import get_db, get_or_create_client_db
from ..models import RoomIn, RoomOut
from ..auth import get_current_user
from .. import crud
# from ..db import get_connection


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

# ---------- Create Room ----------
@router.post("/add", response_model=RoomIn)
def create_room(request: Request, room: RoomIn, user: str = Depends(get_current_user)):
# db = Depends(get_db),
    client_id = get_client_id(request)  # ✅ ADDED
    return crud.create_room(client_id, room)  # ✅ UPDATED

# ---------- Get Vacant Rooms ----------
@router.get("/vacant", response_model=list[RoomOut])
def get_vacant_rooms(request: Request, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)  # ✅ ADDED
    return crud.get_vacant_rooms(client_id)  # ✅ UPDATED

# ----------- Update Room Status i.e. Vacant etc. ------------------
@router.put("/update_status/{room_number}")
def update_room_status(request: Request, room_number: int, status: str):
    client_id = get_client_id(request)  # ✅ ADDED
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ REPLACED get_connection()
    cursor = conn.cursor()
    query = f"UPDATE rooms SET status = {placeholder} WHERE room_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (status, room_number))
    # conn = get_connection()
    # cursor = conn.cursor()
    conn.commit()
    conn.close()
    return {"message": f"Room {room_number} status updated to {status}"}

# Get all rooms
@router.get("/", response_model=list[RoomOut])
def get_all_rooms(request: Request, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)  # ✅ ADDED
    return crud.get_all_rooms(client_id)  # ✅ UPDATED
    # rooms = crud.get_all_rooms(db)
    # return rooms

# ---------- Get Room by ID ----------
@router.get("/{room_id}", response_model=RoomOut)
def get_room(request: Request, room_id: int, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)  # ✅ ADDED
    db_room = crud.get_room(client_id, room_id)  # ✅ UPDATED
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

# ---------- Update Room ----------
@router.put("/update/{room_number}", response_model=RoomOut)
def update_room(request: Request, room_number: int, room: RoomIn, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)  # ✅ ADDED
    print("Received room update:", room.dict())
    updated_room = crud.update_room(client_id,, room_number, room)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated_room

# ---------- Delete Room ----------
@router.delete("/{room_number}")
def delete_room(request: Request, room_number: int, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    print("Calling crud.delete_room")
    result = crud.delete_room(client_id, room_number)
    print("IN ROOMS DELETE ROOM", result)
    if not result:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"}
