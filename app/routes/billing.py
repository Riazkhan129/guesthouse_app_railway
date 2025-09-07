from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..models import BillingIn, BillingOut
from ..auth import get_current_user
from .. import crud

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

# Create a bill
@router.post("/", response_model=BillingOut)
def create_bill(bill: BillingIn, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.create_invoice(db, bill)  # match your CRUD function name

# Get all bills
@router.get("/", response_model=list[BillingOut])
def get_all_bills(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.get_all_invoices(db)

# Get a bill by ID
@router.get("/{bill_id}", response_model=BillingOut)
def get_bill(bill_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    bill = crud.get_invoice_by_id(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

# Delete a bill
@router.delete("/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    success = crud.delete_invoice(db, bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}
