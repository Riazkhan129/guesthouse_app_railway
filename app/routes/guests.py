import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Request
from ..db import get_db
from ..models import GuestIn, GuestOut, GuestUpdate
from ..auth import get_current_user
from .. import crud


router = APIRouter(
    prefix="/guests",
    tags=["Guests"]
)

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

@router.post("/")
def create_guest(request: Request, data: GuestIn):
    client_id = get_client_id(request)
    success = crud.create_guest(client_id, data)
    if success:
        return data
    raise HTTPException(status_code=400, detail="Guest already exists")

@router.get("/search/{nic}")
def search_guest(request: Request, nic: str):
    client_id = get_client_id(request)  # ✅ ADDED
    guest = crud.get_guest(client_id, nic)  # ✅ UPDATED
    if guest:
        return guest
    raise HTTPException(status_code=404, detail="Guest not found")

@router.put("/update/{nic}")
def update_guest(request: Request, nic: str, data: GuestUpdate):
    client_id = get_client_id(request)  # ✅ ADDED
    existing = crud.get_guest(client_id, nic)  # ✅ UPDATED
    if not existing:
        raise HTTPException(status_code=404, detail="Guest not found")
    crud.update_guest(client_id, nic, data.dict(exclude_unset=True))
    return {"message": "Guest updated successfully"}

@router.delete("/delete/{nic}")
def delete_guest(request: Request, nic: str):
    client_id = get_client_id(request)  # ✅ ADDED
    success = crud.delete_guest(client_id, nic)  # ✅ UPDATED
    if success:
        return {"message": "Guest deleted successfully"}
    raise HTTPException(status_code=404, detail="Guest not found")

@router.get("/all")
def get_all(request: Request):
    client_id = get_client_id(request)  # ✅ ADDED
    return crud.get_all_guests(client_id)  # ✅ UPDATED


