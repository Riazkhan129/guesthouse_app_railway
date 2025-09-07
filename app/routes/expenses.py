from fastapi import APIRouter, Depends, HTTPException
from ..db import get_db
from ..auth import get_current_user
from .. import crud
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/expenses", tags=["Expenses"])

# ✅ USE THIS INSTEAD
from ..models import ExpenseCreate, ExpenseOut

#class ExpenseCreate(BaseModel):
#    date: str
#    category: str
#    amount: float
#    notes: str = ""

#class ExpenseOut(ExpenseCreate):
#    id: int

@router.post("/add", response_model=ExpenseOut)
def add_expense(expense: ExpenseCreate, db=Depends(get_db), user: str = Depends(get_current_user)):
    return crud.add_expense(db, expense)

@router.get("/", response_model=List[ExpenseOut])
def get_all_expenses(db=Depends(get_db), user: str = Depends(get_current_user)):
    return crud.get_all_expenses(db)

@router.put("/update/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, expense: ExpenseCreate, db=Depends(get_db), user: str = Depends(get_current_user)):
    return crud.update_expense(db, expense_id, expense)

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db=Depends(get_db), user: str = Depends(get_current_user)):
    crud.delete_expense(db, expense_id)
    return {"message": "Deleted"}
