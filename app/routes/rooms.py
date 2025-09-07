from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
from ..db import get_db
from ..models import RoomIn, RoomOut
from ..auth import get_current_user
from .. import crud
from ..db import get_connection


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

# Create a new room
@router.post("/add", response_model=RoomIn)
def create_room(room: RoomIn, db = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.create_room(db, room)


@router.get("/vacant", response_model=list[RoomOut])
def get_vacant_rooms(user: str = Depends(get_current_user)):
    return crud.get_vacant_rooms()

# ----------- Update Room Status i.e. Vacant etc. ------------------
@router.put("/update_status/{room_number}")
def update_room_status(room_number: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE rooms SET status = ? WHERE room_number = ?", (status, room_number))
    conn.commit()
    conn.close()

    return {"message": f"Room {room_number} status updated to {status}"}

# Get all rooms
@router.get("/", response_model=list[RoomOut])
def get_all_rooms(db = Depends(get_db), user: str = Depends(get_current_user)):
    rooms = crud.get_all_rooms(db)
    return rooms

# Get room by ID
@router.get("/{room_id}", response_model=RoomOut)
def get_room(room_id: int, db = Depends(get_db), user: str = Depends(get_current_user)):
    db_room = crud.get_room(db, room_id)
    if not db_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return db_room

# Update room data from rooms update function

@router.put("/update/{room_number}", response_model=RoomOut)
def update_room(room_number: int, room: RoomIn, db = Depends(get_db), user: str = Depends(get_current_user)):
    print("Received room update:", room.dict())
    updated_room = crud.update_room(db, room_number, room)
    if not updated_room:
        raise HTTPException(status_code=404, detail="Room not found")
    return updated_room

# Delete room
@router.delete("/{room_number}")
def delete_room(room_number: int, db = Depends(get_db), user: str = Depends(get_current_user)):
    print("Calling crud.delete_room")
    result = crud.delete_room(db, room_number)
    print("IN ROOMS DELETE ROOM", result)
    if not result:
        raise HTTPException(status_code=404, detail="Room not found")
    return {"message": "Room deleted successfully"}
