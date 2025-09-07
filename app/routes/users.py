from fastapi import APIRouter, Depends
from ..db import get_db
from .. import crud
from ..auth import get_current_user
from pydantic import BaseModel
from ..models import UserUpdate, UserOut
import sqlite3



router = APIRouter(prefix="/users", tags=["Users"])

class UserCreate(BaseModel):
    name: str
    username: str
    password: str
    role: str

@router.get("/")
def get_users(db=Depends(get_db), user=Depends(get_current_user)):
    return crud.get_all_users(db)

@router.post("/add")
def create_user(user_data: UserCreate, db=Depends(get_db), user=Depends(get_current_user)):
    return crud.create_user(db, user_data)

@router.put("/update/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: sqlite3.Connection = Depends(get_db)):
    return crud.update_user(db, user_id, user_data)


@router.delete("/delete/{user_id}")
def delete_user(user_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    return crud.delete_user(db, user_id)

@router.get("/", response_model=list[UserOut])
def get_all_users(db: sqlite3.Connection = Depends(get_db), user: str = Depends(get_current_user)):
    return crud.get_all_users(db)

