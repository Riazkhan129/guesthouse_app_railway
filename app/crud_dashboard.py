# crud/dashboard.py
from .db import get_or_create_client_db
from datetime import datetime, timedelta
from collections import defaultdict
#from fastapi import HTTPException

# ✅ ADDED: Helper to extract client_id from headers
#def get_client_id(request: Request) -> str:
#    client_id = request.headers.get("X-Client-ID")
#    if not client_id:
#        raise HTTPException(status_code=400, detail="Missing client_id")
#    return client_id

def get_dashboard_data(client_id: str):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    
    today = datetime.today()
    results = []

    print("In CURD_DASHBOARD")
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_str = month_date.strftime("%Y-%m")
        
        # Pending bookings (status = 'booked' and checkin date < today)
        if month_str == today.strftime("%Y-%m"):
            query_pending = f"""
                SELECT COUNT(*) FROM bookings
                WHERE status = 'booked' AND checkin_date < {placeholder}
            """
            cursor.execute(query_pending, (today.strftime("%Y-%m-%d"),))
            pending_bookings = cursor.fetchone()[0]
        else:
            pending_bookings = 0


        # Income from invoices
        query_income = f"""
            SELECT
                COALESCE(SUM(room_charges), 0),
                COALESCE(SUM(meals), 0),
                COALESCE(SUM(laundry), 0),
                COALESCE(SUM(damages), 0),
                COALESCE(SUM(total_amount), 0)
            FROM invoices
            WHERE TO_CHAR(checkout_date, 'YYYY-MM') = {placeholder}
        """ if conn.__class__.__name__ == "connection" else f"""
            SELECT
                IFNULL(SUM(room_charges), 0),
                IFNULL(SUM(meals), 0),
                IFNULL(SUM(laundry), 0),
                IFNULL(SUM(damages), 0),
                IFNULL(SUM(total_amount), 0)
            FROM invoices
            WHERE strftime('%Y-%m', checkout_date) = {placeholder}
        """  # ✅ PostgreSQL vs SQLite switch

        cursor.execute(query_income, (month_str,))
        room_charges, meals, laundry, damages, total_amount = cursor.fetchone()

        # ✅ FIXED: Expenses per category
        query_expenses = f"""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE TO_CHAR(date, 'YYYY-MM') = {placeholder}
            GROUP BY category
        """ if conn.__class__.__name__ == "connection" else f"""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE strftime('%Y-%m', date) = {placeholder}
            GROUP BY category
        """  # ✅ PostgreSQL vs SQLite switch

        cursor.execute(query_expenses, (month_str,))
        expenses_data = cursor.fetchall()
        expenses = {cat: amt for cat, amt in expenses_data}
        total_expenses = sum(expenses.values())

        profit_loss = total_amount - total_expenses

        results.append({
            "month": month_str,
            "pending_bookings": pending_bookings,
            "room_charges": room_charges,
            "meals": meals,
            "laundry": laundry,
            "damages": damages,
            "invoice_total": total_amount,
            "expenses": expenses,
            "total_expenses": total_expenses,
            "profit_loss": profit_loss
        })

    conn.close()
    return results[::-1]  # most recent last
