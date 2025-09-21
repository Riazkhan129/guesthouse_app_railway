from fastapi import APIRouter, Depends, Request
from ..db import get_or_create_client_db
from .. import crud
from ..auth import get_current_user
from pydantic import BaseModel
from ..models import UserUpdate, UserOut
import sqlite3
from typing import List



router = APIRouter(prefix="/users", tags=["Users"])

class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role: str

# ✅ Extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

@router.get("/")
def get_users(request: Request, user=Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.get_all_users(conn)

@router.post("/add")
def create_user( user_data: UserCreate, user=Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.create_user(conn, user_data)
    conn.close()
    return result

@router.put("/update/{user_id}")
def update_user(request: Request, user_id: int, user_data: UserUpdate):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    result = crud.update_user(conn, user_id, user_data)
    conn.close()
    return result

@router.delete("/delete/{user_id}")
def delete_user(request: Request, user_id: int, user=Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    crud.delete_user(conn, user_id)
    conn.close()
    return {"message": "Deleted"}

@router.get("/", response_model=list[UserOut])
def get_all_users(request: Request, user: str = Depends(get_current_user)):
    client_id = get_client_id(request)
    conn, placeholder = get_or_create_client_db(client_id)
    return crud.get_all_users(conn)

