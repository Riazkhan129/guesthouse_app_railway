# routes/dashboard.py
from fastapi import APIRouter, Depends, Request
from ..auth import get_current_user
from ..crud_dashboard import get_dashboard_data

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

@router.get("/monthly")
def monthly_dashboard_data(client_id, user: dict = Depends(get_current_user)):
    return get_dashboard_data()
