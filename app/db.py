# db.py

import os
import sqlite3
import psycopg2  
from contextlib import contextmanager
from cryptography.fernet import Fernet
import sys
import string

# ---------- 🧠 Environment Mode Detection ----------
DB_MODE = os.getenv("DB_MODE", "local")  # ✅ 'local' or 'cloud'

# ---------- Get Available Drives ----------
def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives


# ---------- Create or Find ghms Folder ----------
def find_or_create_ghms_folder():
    drives = get_available_drives()
    for drive in drives:
        ghms_path = os.path.join(drive, "ghms")
        try:
            os.makedirs(ghms_path, exist_ok=True)
            return ghms_path
        except Exception as e:
            print(f"❌ Could not access {ghms_path}: {e}")
    
    raise RuntimeError("❌ Could not create ghms folder on any available drive.")



# ---------- Get DB Connection ----------
def get_connection():
    if DB_MODE == "cloud":
        db_url = os.getenv("DB_URL")  # ✅ Railway PostgreSQL URL
        if not db_url:
            raise RuntimeError("❌ DB_URL environment variable not set")
        try:
            conn = psycopg2.connect(db_url)
            print("✅ Connected to Railway PostgreSQL")
            return conn
        except Exception as e:
            raise RuntimeError(f"❌ Failed to connect to Railway DB: {e}")
    else:
        ghms_folder = find_or_create_ghms_folder()  # ✅ Use client drive logic
        db_path = os.path.join(ghms_folder, "guesthouse.sqlite")  # ✅ Fixed local path
        if not os.path.exists(db_path):
            print("⚠️ Local DB not found. Creating it...")
            initialize_database(db_path)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        print(f"✅ Connected to local SQLite at {db_path}")
        return conn

# ---------- FastAPI Dependency ----------
@contextmanager
def get_db():
    db = get_connection()
    try:
        yield db
    finally:
        db.close()


# 🆕 ADDED: Encrypt password using client-specific key
def encrypt_password(password: str, key: str) -> str:
    fernet = Fernet(key.encode())
    return fernet.encrypt(password.encode()).decode()

# ---------- Create Tables & Insert Default Data ----------
def initialize_database():    
    conn = sqlite3.connect()
    cursor = conn.cursor()

    # ✅ Use correct placeholder syntax
    placeholder = "%s" if DB_MODE == "cloud" else "?"

    # -------- Tables --------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_keys (
            client_id TEXT PRIMARY KEY,
            encryption_key TEXT NOT NULL
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id {"SERIAL PRIMARY KEY" if DB_MODE == "cloud" else "INTEGER PRIMARY KEY AUTOINCREMENT"},
            name TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            nic_passport_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            contact TEXT,
            email TEXT,
            address TEXT,
            nationality TEXT,
            emergency_contact TEXT,
            guest_type TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_number TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nic_passport_number TEXT,
            room_number TEXT,
            checkin_date TEXT,
            checkout_date TEXT,
            status TEXT,
            notes TEXT,
            actual_checkin_time TEXT,
            advance_payment REAL,
            actual_checkout_time TEXT,
            total_payment REAL,
            invoice_id int,
            FOREIGN KEY (nic_passport_number) REFERENCES guests(nic_passport_number)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            timestamp TEXT,
            date TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_id INTEGER,
            nic_passport_number TEXT,
            guest_name TEXT,
            room_number TEXT,
            room_price INTEGER,
            checkin_date TEXT,
            checkout_date TEXT,
            total_nights INTEGER,
            room_charges INTEGER,
            laundry REAL,
            meals REAL,
            damages REAL,
            total_amount REAL,
            booking_id INTEGER,
            FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
        )
    """)

    # -------- Insert Default Users --------

    # ---------- Insert Encryption Key ----------
    cursor.execute(f"SELECT encryption_key FROM client_keys LIMIT 1")
    result = cursor.fetchone()
    # cursor.execute("SELECT encryption_key FROM client_keys WHERE client_id = ?", (client_id,))
    result = cursor.fetchone()

    if result:
        encryption_key = result[0]
        print(f"🔐 Existing encryption key found")
    else:
        encryption_key = Fernet.generate_key().decode()
        cursor.execute(
            f"INSERT INTO client_keys (client_id, encryption_key) VALUES ({placeholder}, {placeholder})",
            ("default_client", encryption_key)
        print(f"🆕 New encryption key generated and saved")

    conn.commit()  # ✅ Commit the key insert immediately

    # -------- Insert Default Users --------
    cursor.execute(f"SELECT COUNT(*) FROM users WHERE username = {placeholder}", ("admin1",))
    if cursor.fetchone()[0] == 0:
        encrypted_pw = encrypt_password('admin1', encryption_key)  # 🔄 CHANGED
        cursor.execute(
            f"INSERT INTO users (username, password, role, name) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
            ("admin1", encrypted_pw, "Front Desk", "Admin One")
        )

    cursor.execute(f"SELECT COUNT(*) FROM users WHERE username = {placeholder}", ("admin2",))
    if cursor.fetchone()[0] == 0:
        encrypted_pw = encrypt_password('admin2', encryption_key)  # 🔄 CHANGED
        cursor.execute(
            f"INSERT INTO users (username, password, role, name) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})",
            ("admin2", encrypted_pw, "Management", "Admin Two")
        )


    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {db_path}")


# ---------- Run only once to initialize ----------
if __name__ == "__main__":
    if DB_MODE == "cloud":
        initialize_database()  # ✅ No path needed for Railway
    else:
        ghms_folder = find_or_create_ghms_folder()  # ✅ Use local drive logic
        db_path = os.path.join(ghms_folder, "guesthouse.sqlite")
        initialize_database(db_path)    
