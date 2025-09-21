from fastapi import APIRouter, Depends, HTTPException
from ..auth import get_current_user
from ..db import get_or_create_client_db
from .. import crud
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/expenses", tags=["Expenses"])

# ✅ USE THIS INSTEAD
from ..models import ExpenseCreate, ExpenseOut

# ✅ Extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

@router.post("/add", response_model=ExpenseOut)
def add_expense(request: Request, expense: ExpenseCreate, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.add_expense(conn, expense)

@router.get("/", response_model=List[ExpenseOut])
def get_all_expenses(request: Request, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.get_all_expenses(conn)

@router.put("/update/{expense_id}", response_model=ExpenseOut)
def update_expense(request: Request, expense_id: int, expense: ExpenseCreate, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.update_expense(conn, expense_id, expense)

@router.delete("/{expense_id}")
def delete_expense(request: Request, expense_id: int, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    crud.delete_expense(conn, expense_id)
    return {"message": "Deleted"}
