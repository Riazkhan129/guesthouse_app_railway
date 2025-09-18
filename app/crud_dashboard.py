# crud/dashboard.py
from .db import get_or_create_client_db
from datetime import datetime, timedelta
from collections import defaultdict

def get_dashboard_data(client_id: str):
    conn, _ = get_or_create_client_db(client_id)  # ✅ Use correct DB
    cursor = conn.cursor()
    
    today = datetime.today()
    results = []

    print("In CURD_DASHBOARD")
    for i in range(12):
        month_date = today.replace(day=1) - timedelta(days=i * 30)
        month_str = month_date.strftime("%Y-%m")
        
        # Pending bookings (status = 'booked' and checkin date < today)
        if month_str == today.strftime("%Y-%m"):
            cursor.execute("""
                SELECT COUNT(*) FROM bookings
                WHERE status = 'booked' AND checkin_date < ?
            """, (today.strftime("%Y-%m-%d"),))
            pending_bookings = cursor.fetchone()[0]
        else:
            pending_bookings = 0


        # Income from invoices
        cursor.execute("""
            SELECT
                IFNULL(SUM(room_charges), 0),
                IFNULL(SUM(meals), 0),
                IFNULL(SUM(laundry), 0),
                IFNULL(SUM(damages), 0),
                IFNULL(SUM(total_amount), 0)
            FROM invoices
            WHERE strftime('%Y-%m', checkout_date) = ?
        """, (month_str,))
        room_charges, meals, laundry, damages, total_amount = cursor.fetchone()

        # Expenses per category
        cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE strftime('%Y-%m', date) = ?
            GROUP BY category
        """, (month_str,))
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
