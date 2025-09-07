from fastapi import APIRouter, HTTPException
#from app.db import get_db
from app.db import get_connection
from datetime import datetime
# from pydantic import BaseModel
from app.models import BookingUpdate

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"]
)

@router.put("/update_booking/{booking_id}")
def update_booking_detail(booking_id: int, update: BookingUpdate):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE bookings
            SET status = ?, actual_checkout_date = ?, total_payment = ?, invoice_id = ?
            WHERE booking_id = ?
        """, (
            update.status,
            update.actual_checkout_date,
            update.total_payment,
            update.invoice_id,
            booking_id
        ))

        conn.commit()
        return {"message": f"Booking {booking_id} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#def update_booking_details(
#    booking_id: int,
#    status: str,
#    actual_checkout_date: str,
#    total_payment: float,
#    invoice_id: int
#):

#cursor.execute("""
#    UPDATE bookings
#    SET status = ?, actual_checkout_date = ?, total_payment = ?, invoice_id = ?
#    WHERE booking_id = ?
#""", (status, actual_checkout_date, total_payment, invoice_id, booking_id))
