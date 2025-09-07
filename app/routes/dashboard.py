# routes/dashboard.py
from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..crud_dashboard import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/monthly")
def monthly_dashboard_data(user: dict = Depends(get_current_user)):
    return get_dashboard_data()
