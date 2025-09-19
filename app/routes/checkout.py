from fastapi import APIRouter, HTTPException, Request
#from app.db import get_db
from app.db import get_or_create_client_db  # ✅ Required for multi-tenant support
from datetime import datetime
# from pydantic import BaseModel
from app.models import BookingUpdate

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)

# ✅ ADDED: Helper to extract client_id from headers
def get_client_id(request: Request) -> str:
    client_id = request.headers.get("X-Client-ID")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    return client_id

@router.put("/update_booking/{booking_id}")
def update_booking_detail(request: Request, booking_id: int, update: BookingUpdate):
    client_id = get_client_id(request)
    try:
        conn, placeholder = get_or_create_client_db(client_id)
        cursor = conn.cursor()

        print("status =", update.status)
        print("actual_checkout_date =", update.actual_checkout_date)
        print("total_payment =", update.total_payment)
        print("invoice_id =", update.invoice_id)
        print("booking_id =", booking_id)

        query = f"""
            UPDATE bookings
            SET status = {placeholder},
                str(actual_checkout_date) = {placeholder},
                total_payment = {placeholder},
                invoice_id = {placeholder}
            WHERE booking_id = {placeholder}
        """  # ✅ Dynamic placeholders

        cursor.execute(query, (
            update.status,
            update.actual_checkout_time,
            update.total_payment,
            update.invoice_id,
            str(booking_id)
        ))

        conn.commit()
        return {"message": f"Booking {booking_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



