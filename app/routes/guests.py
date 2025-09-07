import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from ..db import get_db
from ..models import GuestIn, GuestOut, GuestUpdate
from ..auth import get_current_user
from .. import crud


router = APIRouter(
    prefix="/guests",
    tags=["Guests"]
)

@router.post("/")
def create_guest(data: dict):
    success = crud.create_guest(data)
    if success:
        return data
    raise HTTPException(status_code=400, detail="Guest already exists")

@router.get("/search/{nic}")
def search_guest(nic: str):
    guest = crud.get_guest(nic)
    if guest:
        return guest
    raise HTTPException(status_code=404, detail="Guest not found")

@router.put("/update/{nic}")
def update_guest(nic: str, data: GuestUpdate):
    existing = crud.get_guest(nic)
    if not existing:
        raise HTTPException(status_code=404, detail="Guest not found")
    crud.update_guest(nic, data.dict(exclude_unset=True))
    return {"message": "Guest updated successfully"}

@router.delete("/delete/{nic}")
def delete_guest(nic: str):
    success = crud.delete_guest(nic)
    if success:
        return {"message": "Guest deleted successfully"}
    raise HTTPException(status_code=404, detail="Guest not found")

@router.get("/all")
def get_all():
    return crud.get_all_guests()

