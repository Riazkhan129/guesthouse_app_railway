from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db import get_or_create_client_db
from ..models import BillingIn, BillingOut
from ..auth import get_current_user
from .. import crud

router = APIRouter(
    prefix="/billing",
    tags=["Billing"]
)

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

# Create a bill
@router.post("/", response_model=BillingOut)
def create_bill(request: Request, bill: BillingIn, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.create_invoice(conn, bill)  # match your CRUD function name

# Get all bills
@router.get("/", response_model=list[BillingOut])
def get_all_bills(request: Request, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.get_all_invoices(conn)

# Get a bill by ID
@router.get("/{bill_id}", response_model=BillingOut)
def get_bill(request: Request, bill_id: int, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    bill = crud.get_invoice_by_id(conn, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill

# Delete a bill
@router.delete("/{bill_id}")
def delete_bill(request: Request, bill_id: int, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    success = crud.delete_invoice(conn, bill_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}
