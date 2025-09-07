from fastapi import APIRouter, Depends
from ..auth import get_current_user

router = APIRouter()

@router.get("/reports")

def generate_report(type: str, user: dict = Depends(get_current_user)):
    if user["role"] != "🧑‍💼 Management":
        raise HTTPException(status_code=403, detail="Unauthorized")

    conn = sqlite3.connect("guesthouse.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if type == "Monthly Revenue":
        cur.execute("""
            SELECT strftime('%Y-%m', timestamp) as month, SUM(amount) as total_revenue
            FROM billing
            GROUP BY month ORDER BY month DESC
        """)
    elif type == "Occupancy Rate":
        cur.execute("""
            SELECT strftime('%Y-%m', checkin_date) as month, 
                   COUNT(*) as total_bookings 
            FROM bookings 
            GROUP BY month ORDER BY month DESC
        """)
    elif type == "Guest Summary":
        cur.execute("""
            SELECT nationality, COUNT(*) as total_guests 
            FROM guests GROUP BY nationality
        """)
    elif type == "Expense Breakdown":
        cur.execute("""
            SELECT category, SUM(amount) as total_spent
            FROM expenses GROUP BY category
        """)
    else:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid report type")

    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
