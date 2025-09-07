from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models import StaffIn, StaffOut
from auth import get_current_user
import crud

router = APIRouter(
    prefix="/staff",
    tags=["Staff"]
)

# Create staff
@router.post("/", response_model=StaffOut)
def create_staff(staff: StaffIn, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.create_staff(db, staff)

# Get all staff
@router.get("/", response_model=list[StaffOut])
def get_all_staff(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.get_all_staff(db)

# Get staff by ID
@router.get("/{staff_id}", response_model=StaffOut)
def get_staff(staff_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    staff = crud.get_staff(db, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")
    return staff

# Update staff
@router.put("/{staff_id}", response_model=StaffOut)
def update_staff(staff_id: int, staff: StaffIn, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    updated = crud.update_staff(db, staff_id, staff)
    if not updated:
        raise HTTPException(status_code=404, detail="Staff not found")
    return updated

# Delete staff
@router.delete("/{staff_id}")
def delete_staff(staff_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    result = crud.delete_staff(db, staff_id)
    if not result:
        raise HTTPException(status_code=404, detail="Staff not found")
    return {"message": "Staff deleted successfully"}
