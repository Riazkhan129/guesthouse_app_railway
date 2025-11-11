from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from .. import crud


router = APIRouter(
    prefix="/expensecategories",
    tags=["Expensecategories"]
)

def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

class ExpenseCategoryIn(BaseModel):
    category_name: str
    category_active: bool

@router.get("/categories")
def get_categories(request: Request):
    client_id = get_client_id(request)
    return crud.get_all_expense_categories(client_id)

@router.post("/categories")
def add_category(data: ExpenseCategoryIn, request: Request):
    client_id = get_client_id(request)
    return crud.create_expense_category(client_id, data)

@router.put("/categories/{category_id}")
def update_category(category_id: int, data: ExpenseCategoryIn, request: Request):
    client_id = get_client_id(request)
    return crud.update_expense_category(client_id, category_id, data)

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, request: Request):
    client_id = get_client_id(request)
    return crud.delete_expense_category(client_id, category_id)
