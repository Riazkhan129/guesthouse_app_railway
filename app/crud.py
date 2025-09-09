# app/crud.py

from fastapi import HTTPException
from .db import get_connection
from sqlalchemy.orm import Session
from datetime import datetime, date
from .crypto_utils import encrypt_password
# from .crypto_utils import decrypt_password
#from datetime import datetime
from .models import InvoiceCreate
from passlib.context import CryptContext
from .models import UserCreate, UserLogin, UserOut, Client_keysGet
import hashlib
import sqlite3

#------------- encryption Key ------------


def get_encryption_key(client_id: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT encryption_key FROM client_keys WHERE client_id = ?",
        (client_id,)
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# ---------- ROOMS ----------

def get_vacant_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, type, price, status, notes FROM rooms WHERE status = 'vacant'")
    rooms = cursor.fetchall()
    conn.close()
    return [
        {"room_number": r[0], "type": r[1], "price": r[2], "status": r[3], "notes": r[4]}
        for r in rooms
    ]

def create_room(db, room_data):
    cursor = db.cursor()

    # Check if room already exists
    cursor.execute("SELECT * FROM rooms WHERE room_number = ?", (room_data.room_number,))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    # Insert room if not exists
    cursor.execute("""
        INSERT INTO rooms (room_number, type, price, status, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (room_data.room_number, room_data.type, room_data.price, room_data.status, room_data.notes))
    db.commit()
    return {
        "room_number": room_data.room_number,
        "type": room_data.type,
        "price": room_data.price,
        "status": room_data.status,
        "notes": room_data.notes
    }

def get_all_rooms(db):

    cursor = db.cursor()
    rows = cursor.execute("SELECT room_number, type, price, status, notes FROM rooms").fetchall()

    # Define the column names in the correct order
    columns = ["room_number", "type", "price", "status", "notes"]

    # Manually convert each tuple to a dict
    rooms = [dict(zip(columns, row)) for row in rows]
    return rooms

def get_rooms(db):
    cursor = db.cursor()
    rows = cursor.execute("SELECT * FROM rooms").fetchall()

    # Define the column names in the correct order
    columns = ["room_number", "room_type", "price_per_day", "status", "notes"]

    # Manually convert each tuple to a dict
    rooms = [dict(zip(columns, row)) for row in rows]
    return rooms


def update_room(db, room_number, room_data):
    #conn = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        UPDATE rooms SET room_number=?, type=?, price=?, status=?, notes=?
        WHERE room_number=?
    """, (room_data.room_number, room_data.type, room_data.price, room_data.status, room_data.notes, room_number))
    db.commit()
    # Fetch the updated room
    cursor.execute("SELECT * FROM rooms WHERE room_number = ?", (room_data.room_number,))
    row = cursor.fetchone()
    
    if row:
        return {
            "room_number": row[0],
            "type": row[1],
            "price": row[2],
            "status": row[3],
            "notes": row[4]
        }
    else:
        return None
    
    #conn.close()

def delete_room(db, room_number):
    conn = get_connection()
    print("IN DELETE ROOM", room_number)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM rooms WHERE room_number = ?", (room_number,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0


# ---------- GUESTS ----------

# crud.py

# ✅ Get active booking by NIC
def get_active_booking_by_nic(db, nic_passport_number: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT booking_id, nic_passport_number, room_number, checkin_date, checkout_date, status
        FROM bookings
        WHERE nic_passport_number = ? AND status = 'confirmed'
    """, (nic_passport_number,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "booking_id": row[0],
            "nic_passport_number": row[1],
            "room_number": row[2],
            "checkin_date": row[3],
            "checkout_date": row[4],
            "status": row[5],
            "notes": notes(6)
        }
    return None

# ------------------ Guests -------------
def create_guest(data):
    with get_connection() as conn:
        try:
            conn.execute("""
                INSERT INTO guests (nic_passport_number, name, contact, email, address, nationality, emergency_contact, guest_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["nic_passport_number"], data["name"], data["contact"], data["email"],
                data["address"], data.get("nationality"), data.get("emergency_contact"), data.get("guest_type")
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

def get_guest(nic):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM guests WHERE nic_passport_number = ?", (nic,))
        row = cursor.fetchone()
        if row:
            keys = ["nic_passport_number", "name", "contact", "email", "address", "nationality", "emergency_contact", "guest_type"]
            return dict(zip(keys, row))
        return None

def update_guest(nic: str, data: dict):
    print("in Crud update_guest")
    with get_connection() as conn:
        conn.execute("""
            UPDATE guests
            SET name = ?, contact = ?, email = ?, address = ?, nationality = ?, emergency_contact = ?, guest_type = ?
            WHERE nic_passport_number = ?
        """, (
            data["name"], data["contact"], data["email"], data["address"],
            data.get("nationality"), data.get("emergency_contact"), data.get("guest_type"), nic
        ))
        conn.commit()
        return True

def delete_guest(nic):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM guests WHERE nic_passport_number = ?", (nic,))
        conn.commit()
        return cursor.rowcount > 0

def get_all_guests():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM guests")
        rows = cursor.fetchall()
        keys = ["nic_passport_number", "name", "contact", "email", "address", "nationality", "emergency_contact", "guest_type"]
        return [dict(zip(keys, row)) for row in rows]

# ---------- BOOKINGS ----------
def get_room_stats(checkin_date: str) -> dict:
    with get_connection() as conn:
        # Get total number of rooms
        cursor = conn.execute("SELECT COUNT(*) FROM rooms")
        total_rooms = cursor.fetchone()[0]
        print("total_rooms = ", total_rooms)

        # Debug: show all bookings
        cursor = conn.execute("SELECT booking_id, checkin_date, checkout_date, status FROM bookings")
        for row in cursor.fetchall():
             print(row)

        # Get number of rooms booked or checked-in on the given date
        cursor = conn.execute("""
            SELECT COUNT(*) FROM bookings
            WHERE status IN ('booked', 'checked-in')
            AND date(checkin_date) = ?
            AND date(checkout_date) > ?
        """, (checkin_date, checkin_date))  # same date twice to check overlap

        booked_rooms = cursor.fetchone()[0]
        print("booked_rooms = ", booked_rooms)

        return {
            "total_rooms": total_rooms,
            "booked_rooms": booked_rooms,
            "available_rooms": total_rooms - booked_rooms
        }



def create_booking(data):
    booked = data.get("booked_rooms")
    total = data.get("total_rooms")
    if data["booked_rooms"] >= data["total_rooms"]:
        return {"error": "No rooms available for the selected date"}
    else:
        with get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO bookings (nic_passport_number, room_number, checkin_date, checkout_date, status, notes, advance_payment, total_payment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["nic_passport_number"], data["room_number"], data["checkin_date"],
                data["checkout_date"], data["status"], data.get("notes"), data.get("advance_payment"), data.get("total_payment")
            ))
        
        conn.commit()
        
        return cursor.lastrowid

#-------------
def get_booking(booking_id):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
        row = cursor.fetchone()
        print("ROW = ", row)
        if row:
            keys = [column[0] for column in cursor.description]
            result = dict(zip([column[0] for column in cursor.description], row))
            return result
        return None
#-------------

def get_all_bookings():
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM bookings WHERE status = 'booked'")
        rows = cursor.fetchall()
        print("IN GEL ALL BOOKINGS")
        print("rows in all_bookings = ", rows)
        keys = [description[0] for description in cursor.description]
        return [dict(zip(keys, row)) for row in rows]

def get_today_bookings():
    today = date.today().strftime('%Y-%m-%d')  # format as YYYY-MM-DD
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT 
                b.*, 
                g.name AS guest_name
            FROM bookings b
            JOIN guests g 
              ON b.nic_passport_number = g.nic_passport_number
            WHERE b.status = 'booked' 
              AND date(b.checkin_date) = date(?)
        """, (today,))
        rows = cursor.fetchall()
        print("rows in get_tody_bookings = ", rows)
        keys = [description[0] for description in cursor.description]
        return [dict(zip(keys, row)) for row in rows]

# --- Search single booking by ID ---
def get_booking(booking_id):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM bookings WHERE booking_id = ?", (booking_id,))
        row = cursor.fetchone()
        if row:
            keys = ["nic_passport_number", "room_number", "check_in_date", "check_out_date", "status", "notes"]
            return dict(zip(keys, row))
        return None

# def cancel_booking(booking_id):
def cancel_booking(booking_id: int, room_number: str):
    with get_connection() as conn:
        cursor = conn.execute("UPDATE bookings SET status = ? WHERE booking_id = ?", ("cancelled", booking_id))
         # Set the room status to 'booked'
        conn.execute("""
            UPDATE rooms
            SET status = 'vacant'
            WHERE room_number = ?
        """, (room_number,))

        print("AFTER UPDATE ROOM")
        conn.commit()
        return cursor.rowcount > 0

def get_upcoming_bookings():
    today = datetime.today().strftime('%Y-%m-%d')
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM bookings
            WHERE date(checkin_date) >= date(?)
            ORDER BY checkin_date ASC
        """, (today,))
        rows = cursor.fetchall()
        keys = ["booking_id", "nic_passport_number", "room_number", "checkin_date", "checkout_date", "status", "notes"]
        
        return [dict(zip(keys, row)) for row in rows]

#---------- Get Bokkings by NIC for Guest Report ---------


def get_bookings_by_nic(nic_passport_number: str):
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM bookings
            WHERE nic_passport_number = :nic
        """, {"nic": nic_passport_number})

        rows = cursor.fetchall()
        print("IN CRUD GET BOOKING BY NIC ROWS = ", rows)
        keys = [description[0] for description in cursor.description]
        return [dict(zip(keys, row)) for row in rows]
        # return [dict(row) for row in rows]



# ---------- Check-In ----------

# ------- Checked-In booking --------------

def checkin_booking(booking_id, data):
    with get_connection() as conn:

        # Extract each field from the CheckinData object
        room_number = str(data.room_number)
        checkout_date = str(data.checkout_date)
        actual_checkin_time = str(data.actual_checkin_time)
        advance_payment = float(data.advance_payment)
        status = str(data.status)

        # Now safely bind simple values
        conn.execute("""
            UPDATE bookings SET
                room_number = ?,
                checkout_date = ?,
                actual_checkin_time = ?,
                advance_payment = ?,
                status = ?
            WHERE booking_id = ?
        """, (
            room_number,
            checkout_date,
            actual_checkin_time,
            advance_payment,
            status,
            booking_id
        ))

        conn.execute("""
            UPDATE rooms SET
                status = ?
            WHERE room_number = ?
        """, (status, room_number,))

        conn.commit()
        return True

# --------- Check-Out ---------------checked_in

def get_checkedin_bookings():
    with get_connection() as conn:
        cursor = conn.execute("""
            SELECT * FROM bookings WHERE status = 'checked_in'
        """)
        rows = cursor.fetchall()
        print("GET_CHECKEDIN_BOOKINGS ----- ROWS = ", rows)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

        #return [dict(row) for row in rows]

# ----------- update booking check-out ---------------

def checkout_booking(booking_id, final_payment):
    checkout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE bookings SET
                status = 'checked_out',
                actual_checkout_time = ?,
                total_payment = ?
            WHERE booking_id = ?
        """, (checkout_time, final_payment, booking_id))
        conn.commit()
        return cursor.rowcount > 0


#------- Get Room Price for Checkout --------------

def get_room_by_number(room_number: str):
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM rooms WHERE room_number = ?", (room_number,))
        row = cursor.fetchone()
        columns = [column[0] for column in cursor.description]
    if row:
        return dict(zip(columns, row))  # Return row as dict
    return None

# app/crud/guests_crud.py

def get_guest_name_by_nic(nic: str):
    with get_connection() as conn:
        cursor = conn.execute("SELECT name FROM guests WHERE nic_passport_number = ?", (nic,))
        row = cursor.fetchone()
        if row:
            return {"name": row[0]}
        return None


# ---------- BILLING / INVOICES ----------

# from .db import get_connection
# from .models import InvoiceCreate

  


def create_invoice(invoice_data: InvoiceCreate):
    print("💡 Inside create_invoice with:", invoice_data)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (
                nic_passport_number, guest_name, room_number, room_price,
                checkin_date, checkout_date, total_nights,
                room_charges, laundry, meals, damages, total_amount, booking_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            
            invoice_data.guest_nic,
            invoice_data.guest_name,
            invoice_data.room_number,
            invoice_data.room_price,
            invoice_data.checkin_date,
            invoice_data.checkout_date,
            invoice_data.total_nights,
            invoice_data.room_charges,
            invoice_data.laundry,
            invoice_data.meals,
            invoice_data.damages,
            invoice_data.total_amount,
            invoice_data.booking_id
        ))
        conn.commit()
        invoice_id = cursor.lastrowid
        print("IN CRUD - CREATE_INVOICE = ", invoice_id)
        conn.close()
        return {**invoice_data.dict(), "id": invoice_id}  # returns BillingOut
    except Exception as e:
        print("❌ Error in create_invoice:", str(e))
        raise

def get_all_invoices(db):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, booking_id, amount, date FROM invoices")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "booking_id": row[1], "amount": row[2], "date": row[3]} for row in rows]

def get_invoice_by_id(db, invoice_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, booking_id, amount, date FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "booking_id": row[1], "amount": row[2], "date": row[3]}
    return None

def delete_invoice(db, invoice_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

# ---------- EXPENSES ----------

def add_expense(db, expense):
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, amount, category, notes, date)
        VALUES (?, ?, ?, ?, ?)
    """, (expense.title, expense.amount, expense.category,  expense.notes, expense.date))
    db.commit()
    expense_id = cursor.lastrowid
    return {
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "notes": expense.notes,
        "date": expense.date
        
    }

def get_all_expenses(db):
    cursor = db.cursor()
    rows = cursor.execute("SELECT id, title, amount, category, notes, timestamp, date FROM expenses ORDER BY date DESC").fetchall()
    return [
        {"id": row[0], "title": row[1], "amount": row[2], "category": row[3], "notes": row[4], "timestamp": row[5], "date": row[6],   }
        for row in rows
    ]

def update_expense(db, expense_id, expense):
    cursor = db.cursor()
    print("In Curd - Update_Expense")
    cursor.execute("""
        UPDATE expenses SET title=?, amount=?, category=?,  notes=?, date=?
        WHERE id=?
    """, (expense.title, expense.amount, expense.category,  expense.notes, expense.date, expense_id))
    db.commit()
    return {
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "notes": expense.notes,
        "date": expense.date
    }

def delete_expense(db, expense_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
    db.commit()

# ---------- USERS ----------
#from fastapi import HTTPException
#from passlib.context import CryptContext
#from .models import UserCreate, UserLogin, UserOut
#from .db import get_connection
#import hashlib

# crud.py

    try:
        decrypted = decrypt_password(encrypted_password)
        return decrypted == plain_password
    except Exception as e:
        print("Password decryption failed:", e)
        return False
def verify_password(plain_password: str, encrypted_password: str) -> bool:
    try:
        decrypted = decrypt_password(encrypted_password)
        return decrypted == plain_password
    except Exception as e:
        print("Password decryption failed:", e)
        return False

#---------------------
#from .crypto_utils import encrypt_password

def add_user(db, data):
    password_encrypted = encrypt_password(data["password"])
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)",
        (data["name"], data["username"], password_encrypted, data["role"])
    )
    db.commit()

#---------------
def login_user(user: UserLogin):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, username, password, role FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()

    if not db_user or not verify_password(user.password, db_user[3]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "id": db_user[0],
        "name": db_user[1],
        "username": db_user[2],
        "role": db_user[4]
    }


#-----------------
# from .crypto_utils import encrypt_password

def create_user(db, user_data):
    cursor = db.cursor()

    # Encrypt the password before saving
    encrypted_password = encrypt_password(user_data.password)

    cursor.execute(
        "INSERT INTO users (name, username, password, role) VALUES (?, ?, ?, ?)",
        (user_data.name, user_data.username, encrypted_password, user_data.role)
    )

    db.commit()

    return {"message": "User created successfully", "user_id": cursor.lastrowid}

#-------
# from .crypto_utils import decrypt_password

def get_all_users(db):
    cursor = db.cursor()
    rows = cursor.execute("SELECT user_id, name, username, password, role FROM users").fetchall()
    users = []
    for row in rows:
        try:
            decrypted_password = decrypt_password(row[3])  # row[3] is password
        except Exception as e:
            decrypted_password = "[Error decrypting]"

        users.append({
            "user_id": row[0],
            "name": row[1],
            "username": row[2],
            "password": decrypted_password,  # show in plain text
            "role": row[4]
        })
    return users

#----------------
def update_user(db, user_id, data):
    cursor = db.cursor()

    if data.password:  # If password is provided, encrypt and include in update
        encrypted_password = encrypt_password(data.password)
        cursor.execute(
            "UPDATE users SET name = ?, role = ?, password = ? WHERE user_id = ?",
            (data.name, data.role, encrypted_password, user_id)
        )
    else:  # Password is not being updated
        cursor.execute(
            "UPDATE users SET name = ?, role = ? WHERE user_id = ?",
            (data.name, data.role, user_id)
        )

    db.commit()
    return {"message": "User updated successfully"}


#------------------

def delete_user(db, user_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    db.commit()
    return {"message": "User deleted"}


