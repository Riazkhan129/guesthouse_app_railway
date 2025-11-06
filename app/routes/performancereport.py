from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..db import get_or_create_client_db

router = APIRouter()

router = APIRouter(
    prefix="/performancereport",
    tags=["Performancereport"]
)

# @router.get("/performancereport")

@router.get("/")
def get_performance_report(client_id: str, start_date: str, end_date: str):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED: Receive placeholder
    cursor = conn.cursor()

    # Total rooms
    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]

    # Occupied rooms
       
    query = f"""
    SELECT COUNT(*) FROM bookings
    WHERE actual_checkin_time IS NOT NULL
      AND actual_checkout_time IS NULL
      AND checkin_date BETWEEN {placeholder} AND {placeholder}
    """
    cursor.execute(query, (start_date, end_date))
    occupied_rooms = cursor.fetchone()[0]

    # Revenue
    cursor.execute(f"""
        SELECT COALESCE(SUM(room_rate), 0) FROM bookings
        WHERE actual_checkin_time BETWEEN {placeholder} AND {placeholder}
    """, (start_date, end_date))
    total_revenue = cursor.fetchone()[0]

    # Expenses
    cursor.execute(f"""
        SELECT COALESCE(SUM(amount), 0) FROM expenses
        WHERE date BETWEEN {placeholder} AND {placeholder}
    """, (start_date, end_date))
    total_expenses = cursor.fetchone()[0]

    # Guest demographics
    cursor.execute("""
        SELECT nationality, COUNT(*) FROM guests
        GROUP BY nationality
    """, )
    demographics = cursor.fetchall()

    return {
        "total_rooms": total_rooms,
        "occupied_rooms": occupied_rooms,
        "vacant_rooms": total_rooms - occupied_rooms,
        "occupancy_rate": round((occupied_rooms / total_rooms) * 100, 2) if total_rooms else 0,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": total_revenue - total_expenses,
        "demographics": demographics
    }
