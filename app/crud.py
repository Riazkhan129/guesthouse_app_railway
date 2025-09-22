# app/crud.py

from fastapi import HTTPException
from .db import get_or_create_client_db
from sqlalchemy.orm import Session
from datetime import datetime, date
from .crypto_utils import encrypt_password
# from .crypto_utils import decrypt_password
#from datetime import datetime
from .models import InvoiceCreate, GuestIn
from passlib.context import CryptContext
from .models import UserCreate, UserLogin, UserOut, Client_keysGet
import hashlib
import sqlite3

#------------- encryption Key ------------


def get_encryption_key(client_id: str) -> str:
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED: Receive placeholder
    cursor = conn.cursor()

    query = f"SELECT encryption_key FROM client_keys WHERE client_id = {placeholder}"  # ✅ UPDATED: Dynamic placeholder
    cursor.execute(query, (client_id,))  # ✅ No change needed here
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# ---------- ROOMS ----------

def get_vacant_rooms(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    # conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, type, price, status, notes FROM rooms WHERE status = 'vacant'")
    rooms = cursor.fetchall()
    conn.close()
    return [
        {"room_number": r[0], "type": r[1], "price": r[2], "status": r[3], "notes": r[4]}
        for r in rooms
    ]

def create_room(client_id: str, room_data):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    # cursor = db.cursor()

    # Check if room already exists
    query_check = f"SELECT * FROM rooms WHERE room_number = {placeholder}"
    cursor.execute(query_check, (room_data.room_number,))
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Room number already exists")

    # Insert room if not exists

    query_insert = f"""
        INSERT INTO rooms (room_number, type, price, status, notes)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """  # ✅ Dynamic placeholders
    cursor.execute(query_insert, (
        room_data.room_number,
        room_data.type,
        room_data.price,
        room_data.status,
        room_data.notes
    ))
    conn.commit()
    conn.close()
    return {
        "room_number": room_data.room_number,
        "type": room_data.type,
        "price": room_data.price,
        "status": room_data.status,
        "notes": room_data.notes
    }

def get_all_rooms(client_id: str):
    conn, _ = get_or_create_client_db(client_id)

    cursor = conn.cursor()
    cursor.execute("SELECT room_number, type, price, status, notes FROM rooms")
    rows = cursor.fetchall()
    
    columns = ["room_number", "type", "price", "status", "notes"]
    rooms = [dict(zip(columns, row)) for row in rows]
    return rooms

def get_rooms(client_id: str):
    conn, _ = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms")
    rows = cursor.fetchall()
    columns = ["room_number", "room_type", "price_per_day", "status", "notes"]
    rooms = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return rooms


def update_room(client_id: str, room_number, room_data):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()

    query_update = f"""
        UPDATE rooms SET room_number={placeholder}, type={placeholder}, price={placeholder},
        status={placeholder}, notes={placeholder} WHERE room_number={placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query_update, (
        str(room_data.room_number),
        room_data.type,
        room_data.price,
        room_data.status,
        room_data.notes,
        str(room_number)
    ))
    conn.commit()
    
#    cursor.execute("""
#        UPDATE rooms SET room_number=?, type=?, price=?, status=?, notes=?
#        WHERE room_number=?
#    """, (room_data.room_number, room_data.type, room_data.price, room_data.status, room_data.notes, room_number))
#    conn.commit()
    # Fetch the updated room
    query_fetch = f"SELECT * FROM rooms WHERE room_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query_fetch, (str(room_data.room_number),))
    row = cursor.fetchone()
    conn.close()
    
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

def delete_room(client_id: str, room_number):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED    print("IN DELETE ROOM", room_number)
    cursor = conn.cursor()
    
    query = f"DELETE FROM rooms WHERE room_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (str(room_number),))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0



# ---------- GUESTS ----------

# ✅ Get active booking by NIC
def get_active_booking_by_nic(client_id: str, nic_passport_number: str):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query = f"""
        SELECT booking_id, nic_passport_number, room_number, checkin_date, checkout_date, status
        FROM bookings
        WHERE nic_passport_number = {placeholder} AND status = 'confirmed'
    """  # ✅ Dynamic placeholder
    cursor.execute(query, (nic_passport_number,))
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
def create_guest(client_id: str, data: GuestIn):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    try:
        query = f"""
            INSERT INTO guests (nic_passport_number, name, contact, email, address, nationality, emergency_contact, guest_type)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """  # ✅ Dynamic placeholders
        cursor.execute(query, (
            data.nic_passport_number, data.name, data.contact, data.email,
            data.address, data.nationality, data.emergency_contact, data.guest_type
        ))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_guest(client_id: str, nic: str):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    query = f"SELECT * FROM guests WHERE nic_passport_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (nic,))
    row = cursor.fetchone()
    conn.close()
    if row:
        keys = ["nic_passport_number", "name", "contact", "email", "address", "nationality", "emergency_contact", "guest_type"]
        return dict(zip(keys, row))
    return None

def update_guest(client_id: str, nic: str, data: dict):
    print("in Crud update_guest")
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    query = f"""
        UPDATE guests
        SET name = {placeholder}, contact = {placeholder}, email = {placeholder}, address = {placeholder},
            nationality = {placeholder}, emergency_contact = {placeholder}, guest_type = {placeholder}
        WHERE nic_passport_number = {placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query, (
        data["name"], data["contact"], data["email"], data["address"],
        data.get("nationality"), data.get("emergency_contact"), data.get("guest_type"), nic
    ))
    conn.commit()
    conn.close()
    return True

def delete_guest(client_id: str, nic: str):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"DELETE FROM guests WHERE nic_passport_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (nic,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def get_all_guests(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guests")  # ✅ No placeholder needed
    rows = cursor.fetchall()
    conn.close()
    keys = ["nic_passport_number", "name", "contact", "email", "address", "nationality", "emergency_contact", "guest_type"]
    return [dict(zip(keys, row)) for row in rows]

# ---------- BOOKINGS ----------
def get_room_stats(client_id: str, checkin_date: str) -> dict:
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    
    # Get total number of rooms
    cursor.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cursor.fetchone()[0]
    print("total_rooms = ", total_rooms)

    # Debug: show all bookings
    cursor.execute("SELECT booking_id, checkin_date, checkout_date, status FROM bookings")
    for row in cursor.fetchall():
             print(row)

    # Get number of rooms booked or checked-in on the given date
    query = f"""
        SELECT COUNT(*) FROM bookings
        WHERE status IN ('booked', 'checked-in')
        AND date(checkin_date) = date({placeholder})
        AND date(checkout_date) > date({placeholder})
    """  # ✅ Dynamic placeholders
    cursor.execute(query, (checkin_date, checkin_date))
    booked_rooms = cursor.fetchone()[0]
    print("booked_rooms = ", booked_rooms)

    conn.close()
    return {
        "total_rooms": total_rooms,
        "booked_rooms": booked_rooms,
        "available_rooms": total_rooms - booked_rooms
    }

def create_booking(client_id: str, data: dict):
    booked = data.get("booked_rooms")
    total = data.get("total_rooms")
    if data["booked_rooms"] >= data["total_rooms"]:
        return {"error": "No rooms available for the selected date"}
    else:
        conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
        cursor = conn.cursor()
        query = f"""
            INSERT INTO bookings (
                nic_passport_number, room_number, checkin_date, checkout_date,
                status, notes, advance_payment, total_payment
            )
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """  # ✅ Dynamic placeholders
        cursor.execute(query, (
            data["nic_passport_number"], data["room_number"], data["checkin_date"],
            data["checkout_date"], data["status"], data.get("notes"),
            data.get("advance_payment"), data.get("total_payment")
        ))
        
        conn.commit()
        conn.close()
        return cursor.lastrowid

#-------------
def get_booking(client_id: str, booking_id: int):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"SELECT * FROM bookings WHERE booking_id = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (booking_id,))
    row = cursor.fetchone()
    conn.close()
    print("ROW = ", row)
    if row:
        keys = [column[0] for column in cursor.description]
        result = dict(zip([column[0] for column in cursor.description], row))
        return result
    return None

def get_all_bookings(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE status = 'booked'")
    rows = cursor.fetchall()
    print("IN GEL ALL BOOKINGS")
    print("rows in all_bookings = ", rows)
    keys = [description[0] for description in cursor.description]
    return [dict(zip(keys, row)) for row in rows]

def get_today_bookings(client_id: str):
    today = date.today().strftime('%Y-%m-%d')  # format as YYYY-MM-DD
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"""
        SELECT 
            b.*, 
            g.name AS guest_name
        FROM bookings b
        JOIN guests g 
          ON b.nic_passport_number = g.nic_passport_number
        WHERE b.status = 'booked' 
          AND date(b.checkin_date) = date({placeholder})
    """  # ✅ Dynamic placeholder
    cursor.execute(query, (today,))
    rows = cursor.fetchall()
    print("rows in get_tody_bookings = ", rows)
    keys = [description[0] for description in cursor.description]
    conn.close()
    return [dict(zip(keys, row)) for row in rows]

# --- Search single booking by ID ---
def get_booking(client_id: str, booking_id: int):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED: Use tenant-aware DB
    cursor = conn.cursor()
    query = f"SELECT * FROM bookings WHERE booking_id = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (booking_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        keys = ["nic_passport_number", "room_number", "check_in_date", "check_out_date", "status", "notes"]
        return dict(zip(keys, row))
    return None

# def cancel_booking(booking_id):
def cancel_booking(client_id: str, booking_id: int, room_number: str):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()

    query_cancel = f"UPDATE bookings SET status = 'cancelled' WHERE booking_id = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query_cancel, (booking_id,))         # Set the room status to 'booked'
    booking_updated = cursor.rowcount
    print("booking_updated =", booking_updated)  # ✅ DEBUG

    # query_room = f"UPDATE rooms SET status = 'vacant' WHERE room_number = {placeholder}"  # ✅ Dynamic placeholder
    # cursor.execute(query_room, (str(room_number),))
    # room_updated = cursor.rowcount
    # print("room_updated =", room_updated)  # ✅ DEBUG

    # print("AFTER UPDATE ROOM")
    conn.commit()
    conn.close()
    
    return booking_updated > 0 and room_updated > 0
    # return cursor.rowcount > 0

def get_upcoming_bookings(client_id: str):
    today = datetime.today().strftime('%Y-%m-%d')
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"""
        SELECT * FROM bookings
        WHERE date(checkin_date) >= date({placeholder})
        ORDER BY checkin_date ASC
    """  # ✅ Dynamic placeholder
    cursor.execute(query, (today,))
    rows = cursor.fetchall()
    keys = ["booking_id", "nic_passport_number", "room_number", "checkin_date", "checkout_date", "status", "notes"]
        
    return [dict(zip(keys, row)) for row in rows]

    
#---------- Get Bokkings by NIC for Guest Report ---------

def get_bookings_by_nic(client_id: str, nic_passport_number: str):
    onn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"""
        SELECT * FROM bookings
        WHERE nic_passport_number = {placeholder}
    """  # ✅ Dynamic placeholder
    cursor.execute(query, (nic_passport_number,))
    rows = cursor.fetchall()
    print("IN CRUD GET BOOKING BY NIC ROWS = ", rows)
    keys = [description[0] for description in cursor.description]
    conn.close()
    return [dict(zip(keys, row)) for row in rows]
    
# ------- Checked-In booking --------------

def checkin_booking(client_id: str, booking_id: int, data):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    
    # Extract each field from the CheckinData object
    room_number = str(data.room_number)
    checkout_date = str(data.checkout_date)
    actual_checkin_time = str(data.actual_checkin_time)
    advance_payment = float(data.advance_payment)
    status = str(data.status)

        # Now safely bind simple values
    query_booking = f"""
    UPDATE bookings SET
        room_number = {placeholder},
        checkout_date = {placeholder},
        actual_checkin_time = {placeholder},
        advance_payment = {placeholder},
        status = {placeholder}
        WHERE booking_id = {placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query_booking, (
        room_number,
        checkout_date,
        actual_checkin_time,
        advance_payment,
        status,
        booking_id
    ))

    query_room = f"""
        UPDATE rooms SET
            status = {placeholder}
        WHERE room_number = {placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query_room, (status, room_number))

    conn.commit()
    conn.close()
    return True

# --------- Check-In ---------------

def get_checkedin_bookings(client_id: str):
    conn, _ = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE status = 'checked_in'")
    rows = cursor.fetchall()
    print("GET_CHECKEDIN_BOOKINGS ----- ROWS = ", rows)
    columns = [column[0] for column in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]
    
# ----------- check-out ---------------

def checkout_booking(client_id: str, booking_id: int, final_payment: float):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    checkout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    query = f"""
        UPDATE bookings SET
            status = 'checked_out',
            actual_checkout_date = {placeholder},
            total_payment = {placeholder}
        WHERE booking_id = {placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query, (checkout_time, final_payment, booking_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

#------- Get Room Price for Checkout --------------

def get_room_by_number(client_id: str, room_number: str):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"SELECT * FROM rooms WHERE room_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (room_number,))
    row = cursor.fetchone()
    columns = [column[0] for column in cursor.description]
    conn.close()
    if row:
        return dict(zip(columns, row))  # Return row as dict
    return None

# ---------- GUEST NAME BY NIC ----------

def get_guest_name_by_nic(client_id: str, nic: str):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"SELECT name FROM guests WHERE nic_passport_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (nic,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"name": row[0]}
    return None
    
# ---------- BILLING / INVOICES ----------

def create_invoice(client_id: str, invoice_data: InvoiceCreate):
    print("💡 Inside create_invoice with:", invoice_data)
    try:
        conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
        cursor = conn.cursor()
        query = f"""
            INSERT INTO invoices (
                nic_passport_number, guest_name, room_number, room_price,
                checkin_date, checkout_date, total_nights,
                room_charges, laundry, meals, damages, total_amount, booking_id
            )
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder})
        """  # ✅ Dynamic placeholders
        cursor.execute(query, (
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

def get_all_invoices(client_id: str):
    conn, _ = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    cursor.execute("SELECT id, booking_id, amount, date FROM invoices")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "booking_id": row[1], "amount": row[2], "date": row[3]} for row in rows]

def get_invoice_by_id(client_id: str, invoice_id: int):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    query = f"SELECT id, booking_id, amount, date FROM invoices WHERE id = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (invoice_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "booking_id": row[1], "amount": row[2], "date": row[3]}
    return None

def delete_invoice(client_id: str, invoice_id: int):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    query = f"DELETE FROM invoices WHERE id = {placeholder}"  # ✅ Dynamic placeholder
    cursor = conn.cursor()
    cursor.execute(query, (invoice_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

# ---------- EXPENSES ----------

def add_expense(client_id: str, expense):
    cursor = conn.cursor()
    conn, placeholder = get_or_create_client_db(client_id)
    query = f"""
        INSERT INTO expenses (title, amount, category, notes, date)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """  # ✅ Dynamic placeholders
    # cursor = conn.cursor()
    cursor.execute(query, (expense.title, expense.amount, expense.category, expense.notes, expense.date))
    conn.commit()
    expense_id = cursor.lastrowid
    return {
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "notes": expense.notes,
        "date": expense.date
        
    }

def get_all_expenses(conn):
    # conn, _ = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, amount, category, notes, timestamp, date FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    return [
        {"id": row[0], "title": row[1], "amount": row[2], "category": row[3], "notes": row[4], "timestamp": row[5], "date": row[6],   }
        for row in rows
    ]



def update_expense(client_id: str, expense_id: int, expense):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    query = f"""
        UPDATE expenses SET title={placeholder}, amount={placeholder}, category={placeholder}, notes={placeholder}, date={placeholder}
        WHERE id={placeholder}
    """  # ✅ Dynamic placeholders
    cursor = conn.cursor()
    cursor.execute(query, (expense.title, expense.amount, expense.category, expense.notes, expense.date, expense_id))
    conn.commit()
    conn.close()
    return {
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category,
        "notes": expense.notes,
        "date": expense.date
    }

def delete_expense(client_id: str, expense_id: int):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    query = f"DELETE FROM expenses WHERE id={placeholder}"  # ✅ Dynamic placeholder
    cursor = conn.cursor()
    cursor.execute(query, (expense_id,))
    conn.commit()
    conn.close()

# ---------- USERS ----------


#    try:
#        decrypted = decrypt_password(encrypted_password)
#        return decrypted == plain_password
#    except Exception as e:
#        print("Password decryption failed:", e)
#        return False
def verify_password(plain_password: str, encrypted_password: str) -> bool:
    try:
        decrypted = decrypt_password(encrypted_password)
        return decrypted == plain_password
    except Exception as e:
        print("Password decryption failed:", e)
        return False

#---------------------

def add_user(client_id: str, data):
    conn, placeholder = get_or_create_client_db(client_id)
    password_encrypted = encrypt_password(data["password"])
    query = f"INSERT INTO users (name, username, password, role) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
    cursor = conn.cursor()
    cursor.execute(query, (data["name"], data["username"], password_encrypted, data["role"]))
    conn.commit()
    conn.close()

#---------------
def login_user(client_id: str, user: UserLogin):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()

    query = f"SELECT user_id, username, password, role FROM users WHERE username = {placeholder}"  # ✅ Dynamic placeholder
    cursor = conn.cursor()
    cursor.execute(query, (user.username,))
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

def create_user(client_id: str, user_data):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    encrypted_password = encrypt_password(user_data.password)

    query = f"INSERT INTO users (name, username, password, role) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})"
    cursor = conn.cursor()
    cursor.execute(query, (user_data.name, user_data.username, encrypted_password, user_data.role))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {"message": "User created successfully", "user_id": cursor.lastrowid}

#-------

def get_all_users(conn):
    # conn, _ = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, username, password, role FROM users")
    rows = cursor.fetchall()
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
    #conn.close()
    return users

#----------------
def update_user(client_id: str, user_id: int, data):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    if data.password:
        encrypted_password = encrypt_password(data.password)
        query = f"UPDATE users SET name={placeholder}, role={placeholder}, password={placeholder} WHERE user_id={placeholder}"
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


