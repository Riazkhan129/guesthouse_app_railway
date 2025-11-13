# app/crud.py

from fastapi import HTTPException
from .db import get_or_create_client_db
from sqlalchemy.orm import Session
from datetime import datetime, date
# from .crypto_utils import encrypt_password
# from .crypto_utils import decrypt_password
#from datetime import datetime
from .models import InvoiceCreate, GuestIn
from passlib.context import CryptContext
from .models import UserCreate, UserLogin, UserOut, Client_keysGet, RoomServiceRequestIn, RoomServiceRequestOut, RoomServiceSummaryOut
import hashlib
import sqlite3
from cryptography.fernet import Fernet



def decrypt_password(encrypted_password: str, key: str) -> str:
    fernet = Fernet(key.encode())  # Ensure key is in bytes
    return fernet.decrypt(encrypted_password.encode()).decode()

#------------- encryption Key ------------


def get_encryption_key(client_id: str) -> str:
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED: Receive placeholder
    cursor = conn.cursor()

    query = f"SELECT encryption_key FROM client_keys WHERE client_id = {placeholder}"  # ✅ UPDATED: Dynamic placeholder
    cursor.execute(query, (client_id,))  # ✅ No change needed here
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

# ------- Expense Categories --------------


def get_all_expense_categories(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category_name, category_active FROM expense_categories")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],  # ✅ renamed from category_id
            "category_name": row[1],
            "category_active": row[2]
        }
        for row in rows
    ]



def create_expense_category(client_id: str, category_data):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    print("Received category_data in CRUD:", category_data)
    # Check if category already exists
    query_check = f"SELECT * FROM expense_categories WHERE category_name = {placeholder}"
    cursor.execute(query_check, (category_data.category_name,))
    print("Received category_data in CRUD: AFTER SELECT")
    existing = cursor.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Expense category already exists")

    # Insert new category
    query_insert = f"""
        INSERT INTO expense_categories (category_name, category_active)
        VALUES ({placeholder}, {placeholder})
    """
    cursor.execute(query_insert, (
        category_data.category_name,
        category_data.category_active
    ))
    print("Received category_data in CRUD: AFTER INSERT")
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()

    return {
        "id": category_id,
        "category_name": category_data.category_name,
        "category_active": category_data.category_active
    }


def update_expense_category(client_id: str, id: int, category_data):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query_update = f"""
        UPDATE expense_categories
        SET category_name = {placeholder}, category_active = {placeholder}
        WHERE id = {placeholder}
    """
    cursor.execute(query_update, (
        category_data.category_name,
        category_data.category_active,
        id
        
    ))
    conn.commit()
    conn.close()

    return {
        "id": id,
        "category_name": category_data.category_name,
        "category_active": category_data.category_active
    }


def delete_expense_category(client_id: str, category_id: int):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query_delete = f"""
        DELETE FROM expense_categories WHERE id = {placeholder}
    """
    cursor.execute(query_delete, (category_id,))
    conn.commit()
    conn.close()

    return {"message": "Expense category deleted"}

#------------ Expense Items

def create_expense_item(client_id: str, item_data):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query_insert = f"""
        INSERT INTO expense_items (category_id, expense_name, default_price, unit, is_activated, created)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """
    now = datetime.now().isoformat()
    cursor.execute(query_insert, (
        item_data.category_id,
        item_data.expense_name,
        item_data.default_price,
        item_data.unit,
        item_data.is_activated,
        now
    ))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()

    return {
        "expense_item_id": item_id,
        "category_id": item_data.category_id,
        "expense_name": item_data.expense_name,
        "default_price": item_data.default_price,
        "unit": item_data.unit,
        "is_activated": item_data.is_activated,
        "created": now
    }

def get_all_expense_items(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expense_items")
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "expense_item_id": row[0],
            "category_id": row[1],
            "expense_name": row[2],
            "default_price": row[3],
            "unit": row[4],
            "is_activated": bool(row[5]),
            "created": row[6]
        }
        for row in rows
    ]

def get_expense_items_by_category(client_id: str, category_id: int):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    print("IN CRUD get_expense_items_by_category")
    cursor.execute(
        "SELECT * FROM expense_items WHERE category_id = ?", (category_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "expense_item_id": row[0],
            "category_id": row[1],
            "expense_name": row[2],
            "default_price": row[3],
            "unit": row[4],
            "is_activated": bool(row[5]),
            "created": row[6]
        }
        for row in rows
    ]


def get_expense_item_by_id(client_id: str, item_id: int):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    query = f"SELECT * FROM expense_items WHERE expense_item_id = {placeholder}"
    cursor.execute(query, (item_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Expense item not found")

    return {
        "expense_item_id": row[0],
        "category_id": row[1],
        "expense_name": row[2],
        "default_price": row[3],
        "unit": row[4],
        "is_activated": bool(row[5]),
        "created": row[6]
    }

def update_expense_item(client_id: str, item_id: int, item_data):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query = f"""
        UPDATE expense_items
        SET category_id = {placeholder}, expense_name = {placeholder},
            default_price = {placeholder}, unit = {placeholder},
            is_activated = {placeholder}
        WHERE expense_item_id = {placeholder}
    """
    cursor.execute(query, (
        item_data.category_id,
        item_data.expense_name,
        item_data.default_price,
        item_data.unit,
        item_data.is_activated,
        item_id
    ))
    conn.commit()
    conn.close()

    return {
        "expense_item_id": item_id,
        "category_id": item_data.category_id,
        "expense_name": item_data.expense_name,
        "default_price": item_data.default_price,
        "unit": item_data.unit,
        "is_activated": item_data.is_activated,
        "created": datetime.now().isoformat()
    }

def delete_expense_item(client_id: str, item_id: int):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    query = f"DELETE FROM expense_items WHERE expense_item_id = {placeholder}"
    cursor.execute(query, (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Expense item deleted"}





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


def get_checkedin_rooms(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    cursor.execute("SELECT room_number, type, price, status, notes FROM rooms WHERE status = 'checked_in'")
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
    
    query_fetch = f"SELECT * FROM rooms WHERE room_number = {placeholder}"  
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
    conn, placeholder = get_or_create_client_db(client_id)  
    cursor = conn.cursor()
    
    query = f"DELETE FROM rooms WHERE room_number = {placeholder}"  
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
            INSERT INTO guests (nic_passport_number, name, contact, email, address, nationality, emergency_contact, guest_type, corporate_name, corporate_contact_person, corporate_address)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """  # ✅ Dynamic placeholders
        cursor.execute(query, (
            data.nic_passport_number, data.name, data.contact, data.email,
            data.address, data.nationality, data.emergency_contact, data.guest_type,
            data.corporate_name, data.corporate_contact_person, data.corporate_address
            
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
    print("ROWS = ", row)
    conn.close()
    if row:
        keys = ["nic_passport_number", "name", "contact", "email", "address", "nationality", "emergency_contact", "guest_type",
                "corporate_name", "corporate_contact_person", "corporate_address"]
        
        return dict(zip(keys, row))
    return None

def update_guest(client_id: str, nic: str, data: dict):
    print("in Crud update_guest")
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    query = f"""
        UPDATE guests
        SET name = {placeholder}, contact = {placeholder}, email = {placeholder}, address = {placeholder},
            nationality = {placeholder}, emergency_contact = {placeholder}, guest_type = {placeholder},
            corporate_name = {placeholder}, corporate_contact_person = {placeholder}, corporate_address = {placeholder}
        WHERE nic_passport_number = {placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query, (
        data["name"], data["contact"], data["email"], data["address"],
        data.get("nationality"), data.get("emergency_contact"), data.get("guest_type"),
        data.get("corporate_name"), data.get("corporate_contact_person"), data.get("corporate_address"), nic
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
    keys = ["nic_passport_number", "name", "contact", "email", "address", "nationality", "emergency_contact", "guest_type",
            "corporate_name", "corporate_contact_person", "corporate_address"]
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
                status, notes, advance_payment, total_payment, corporate_name
            )
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder})
        """  # ✅ Dynamic placeholders
        cursor.execute(query, (
            data["nic_passport_number"], data["room_number"], data["checkin_date"],
            data["checkout_date"], data["status"], data.get("notes"), 
            data.get("advance_payment"), data.get("total_payment"), data.get("corporate_name")
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
        keys = ["nic_passport_number", "room_number", "check_in_date", "check_out_date", "status", "notes", "corporate_name"]
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

    conn.commit()
    conn.close()

    return booking_updated > 0


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
    print("ROWN IN CRUD.Get_Upcoming_Bookint === ", rows)
    # keys = ["booking_id", "nic_passport_number", "checkin_date", "checkout_date", "status", "corporate_name"]
        
    # return [dict(zip(keys, row)) for row in rows]
    keys = [description[0] for description in cursor.description]
    return [dict(zip(keys, row)) for row in rows]


#---------- Get Bokkings by NIC for Guest Report ---------

def get_bookings_by_nic(client_id: str, nic_passport_number: str):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
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
    print("✅ Received check-in payload:", data)
    print("MODE OF PAYMENT -- ",data.mode_of_payment)
    print("PROFESSIONN -- ", data.profession)
    print("PURPOSE OF VISIT --- ", data.purpose_of_visit)
    
    # Extract each field from the CheckinData object
    room_number = str(data.room_number)
    room_type = str(data.room_type)
    room_rate = int(data.room_rate) 
    companions = int(data.companions)
    mode_of_payment = str(data.mode_of_payment)
    profession = str(data.profession)
    purpose_of_visit = str(data.purpose_of_visit)
    actual_checkin_time = str(data.actual_checkin_time)
    checkout_date = str(data.checkout_date)
    advance_payment = float(data.advance_payment)
    status = str(data.status)

        # Now safely bind simple values
    query_booking = f"""
    UPDATE bookings SET
        room_number = {placeholder},
        room_type = {placeholder},
        room_rate = {placeholder},
        companions = {placeholder},
        mode_of_payment = {placeholder},
        profession = {placeholder},
        purpose_of_visit = {placeholder},
        actual_checkin_time = {placeholder},
        checkout_date = {placeholder},
        advance_payment = {placeholder},
        status = {placeholder}
        WHERE booking_id = {placeholder}
    """  # ✅ Dynamic placeholders
    cursor.execute(query_booking, (
        room_number,
        room_type,
        room_rate,
        companions,
        mode_of_payment,
        profession,
        purpose_of_visit,
        actual_checkin_time,
        checkout_date,
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
    print("From get_checkedin_bookings GET_CHECKEDIN_BOOKINGS ----- ROWS = ", rows)
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
    query = f"SELECT name, nic_passport_number, address, corporate_name, nationality, contact, emergency_contact, email  FROM guests WHERE nic_passport_number = {placeholder}"  # ✅ Dynamic placeholder
    cursor.execute(query, (nic,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "name": row[0],
            "nic_passport_number": row[1],
            "address": row[2],
            "corporate_name": row[3],
            "nationality": row[4],
            "contact": row[5],
            "emergency_contact": row[6],
            "email": row[7]
          }
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
            RETURNING invoice_id
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
        invoice_id = cursor.fetchone()[0]
        conn.commit()
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

# ---------- EXPENSES ---------------

def get_all_expenses(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query = f"""
        SELECT 
            e.expense_id AS expense_id,
            e.category_id,
            c.category_name,
            e.expense_item_id,
            i.expense_name,
            e.amount,
            e.notes,
            e.timestamp,
            e.date
        FROM expenses e
        JOIN expense_categories c ON e.category_id = c.id
        JOIN expense_items i ON e.expense_item_id = i.expense_item_id
        ORDER BY e.date DESC
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "expense_id": row[0],
            "category_id": row[1],
            "category_name": row[2],
            "expense_item_id": row[3],
            "expense_name": row[4],
            "amount": row[5],
            "notes": row[6],
            "timestamp": row[7],
            "date": row[8],
        }
        for row in rows
    ]




def update_expense(client_id: str, expense_id: int, expense):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    query = f"""
        UPDATE expenses SET
            amount = {placeholder},
            notes = {placeholder},
            timestamp = {placeholder},
            date = {placeholder}
        WHERE expense_id = {placeholder}
    """
    cursor.execute(query, (
        expense.amount,
        expense.notes,
        expense.timestamp,
        expense.date,
        expense_id
    ))
    conn.commit()

    # ✅ Fetch full updated record with joins
    query_fetch = """
        SELECT 
            e.expense_id,
            e.category_id,
            c.category_name,
            e.expense_item_id,
            i.expense_name,
            e.amount,
            e.notes,
            e.timestamp,
            e.date
        FROM expenses e
        JOIN expense_categories c ON e.category_id = c.id
        JOIN expense_items i ON e.expense_item_id = i.expense_item_id
        WHERE e.expense_id = ?
    """
    cursor.execute(query_fetch, (expense_id,))
    row = cursor.fetchone()
    conn.close()

    return {
        "expense_id": row[0],
        "category_id": row[1],
        "category_name": row[2],
        "expense_item_id": row[3],
        "expense_name": row[4],
        "amount": row[5],
        "notes": row[6],
        "timestamp": row[7],
        "date": row[8],
    }


# expense.category_id,
#        expense.expense_item_id,

def delete_expense(client_id: str, expense_id: int):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    query = f"DELETE FROM expenses WHERE expense_id={placeholder}"
    cursor.execute(query, (expense_id,))
    conn.commit()
    conn.close()


# ---------- USERS ----------

def verify_password(plain_password: str, encrypted_password: str) -> bool:
    try:
        decrypted = decrypt_password(encrypted_password)
        return decrypted == plain_password
    except Exception as e:
        print("Password decryption failed:", e)
        return False


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


def get_all_users(client_id: str, conn):
    # conn, _ = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, username, password, role FROM users")
    rows = cursor.fetchall()

    key = get_encryption_key(client_id)

    if not key:
        raise ValueError(f"❌ No encryption key found for client_id: {client_id}")
     
    users = []
    for row in rows:
        try:
            decrypted_password = decrypt_password(row[3], key)  # row[3] is password
            print("DECRYPTED PASSWORD ===", decrypted_password)
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
def update_user(client_id: str, user_id: int, data, conn):
    conn, placeholder = get_or_create_client_db(client_id)  # ✅ UPDATED
    cursor = conn.cursor()
    if data.password:
        encrypted_password = encrypt_password(data.password)
        cursor.execute(
        f"UPDATE users SET name = {placeholder}, role = {placeholder}, password = {placeholder} WHERE user_id = {placeholder}",
        (data.name, data.role, encrypted_password, user_id)
        
        )

    conn.commit()
    return {"message": "User updated successfully"}


def delete_user(client_id: str, user_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    return {"message": "User deleted"}

# ----------- Room Service ----------------------------

def get_checkedin_bookings_with_guest(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()
    print("IN GET_CHECKEDIN_BOOKING_WITH_GUEST")

    cursor.execute("""
        SELECT b.booking_id, b.room_number, b.nic_passport_number, g.name
        FROM bookings b
        JOIN guests g ON b.nic_passport_number = g.nic_passport_number
        WHERE b.status = 'checked_in'
    """)
    rows = cursor.fetchall()
    print("GET_CHECKEDIN_BOOKINGS_WITH_GUEST ----- ROWS = ", rows)

    columns = [column[0] for column in cursor.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

#---------- Room Service ------------

def create_room_service_request(client_id: str, data: RoomServiceRequestIn):
    conn, placeholder = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    now = datetime.now().isoformat()
    total_price = data.quantity * data.unit_price  

    print("IN CRUD CREATE_ROOM_SERVICE_REQUEST")
    cursor.execute("""
        INSERT INTO room_service (
            room_id, nic_passport_number, category_id, expense_item_id, quantity, unit_price, total_price,
            requested_at, notes, status, booking_id
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}}
    """, (
        data.room_id, data.nic_passport_number, data.category_id, data.expense_item_id, data.quantity, data.unit_price,
        total_price, now, data.notes, data.status, data.booking_id
    ))

    conn.commit()
    item_id = cursor.lastrowid
    conn.close()

    return {
        "id": item_id,
        "room_id": data.room_id,
        "nic_passport_number": data.nic_passport_number,
        "category_id": data.category_id,
        "expense_item_id": data.expense_item_id,
        "quantity": data.quantity,
        "unit_price": data.unit_price,
        "total_price": total_price,
        "requested_at": now,
        "notes": data.notes,
        "status": data.status
    }


def get_open_roomservice_requests(client_id: str):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            rs.id,
            rs.booking_id,
            rs.room_id,
            rs.nic_passport_number,
            rs.category_id,
            rs.expense_item_id,
            rs.quantity,
            rs.unit_price,
            rs.total_price,
            rs.notes,
            rs.requested_at
        FROM room_service rs
        WHERE rs.status IS NULL OR rs.status = 'Open'
        ORDER BY rs.requested_at DESC
    """)

    rows = cursor.fetchall()
    print("CRUD get_open_roomservice_requests rows = ", rows)
    columns = [column[0] for column in cursor.description]
    conn.close()

    return [dict(zip(columns, row)) for row in rows]

def update_room_service_status(client_id: str, service_id: int, status: str) -> bool:
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE room_service
        SET status = ?
        WHERE id = ?
    """, (status, service_id))

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    return updated > 0


# 🔄 NEW FUNCTION: Group room service by category for a booking

def get_roomservice_summary_by_booking(client_id: str, booking_id: int):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ec.category_name, SUM(rs.total_price) as total_amount
        FROM room_service rs
        JOIN expense_categories ec ON rs.category_id = ec.id
        WHERE rs.booking_id = ? AND (rs.status IS NULL OR rs.status != 'Canceled')
        GROUP BY rs.category_id
    """, (booking_id,))

    rows = cursor.fetchall()
    conn.close()

    return [{"category_name": row[0], "total_amount": row[1]} for row in rows]

def get_roomservice_items_by_booking(client_id: str, booking_id: int):
    conn, _ = get_or_create_client_db(client_id)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            DATE(rs.requested_at) as service_date,
            ec.category_name,
            ei.expense_name,
            rs.total_price
        FROM room_service rs
        JOIN expense_categories ec ON rs.category_id = ec.id
        JOIN expense_items ei ON rs.expense_item_id = ei.expense_item_id
        WHERE rs.booking_id = ? AND (rs.status IS NULL OR rs.status != 'Canceled')
        ORDER BY DATE(rs.requested_at), ec.category_name
    """, (booking_id,))

    rows = cursor.fetchall()
    conn.close()

    # Group by date
    grouped = {}
    for date, category, item, amount in rows:
        if date not in grouped:
            grouped[date] = []
        grouped[date].append({
            "category_name": category,
            "expense_name": item,
            "total_price": amount
        })

    return [{"date": date, "items": grouped[date]} for date in grouped]
