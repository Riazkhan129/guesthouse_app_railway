from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime
#from utils.db import get_or_create_client_db
#from utils.auth import get_client_id


router = APIRouter(
    prefix="/expenseitems",
    tags=["Expenseitems"]
)

def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

class ExpenseItemIn(BaseModel):
    category_id: int
    expense_name: str
    default_price: float
    unit: str
    is_activated: bool

@router.post("/expense_categories/items")
def create_item(data: ExpenseItemIn, request: Request):
    client_id = get_client_id(request)
    from app.crud import create_expense_item
    return create_expense_item(client_id, data)

@router.get("/expense_categories/items")
def get_all_items(request: Request):
    client_id = get_client_id(request)
    from app.crud import get_all_expense_items
    return get_all_expense_items(client_id)

@router.get("/expense_categories/items/by_category/{category_id}")
def get_items_by_category(category_id: int, request: Request):
    client_id = get_client_id(request)
    from app.crud import get_expense_items_by_category
    return get_expense_items_by_category(client_id, category_id)

@router.get("/expense_categories/items/{item_id}")
def get_item_by_id(item_id: int, request: Request):
    client_id = get_client_id(request)
    from app.crud import get_expense_item_by_id
    return get_expense_item_by_id(client_id, item_id)

@router.put("/expense_categories/items/{item_id}")
def update_item(item_id: int, data: ExpenseItemIn, request: Request):
    client_id = get_client_id(request)
    from app.crud import update_expense_item
    return update_expense_item(client_id, item_id, data)

@router.delete("/expense_categories/items/{item_id}")
def delete_item(item_id: int, request: Request):
    client_id = get_client_id(request)
    from app.crud import delete_expense_item
    return delete_expense_item(client_id, item_id)
