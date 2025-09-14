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

# ---------- 🔧 ADDED: Create PostgreSQL DB for client ----------
def create_postgres_database(client_code):
    admin_url = os.getenv("DB_ADMIN_URL")  # Connects to Railway's default 'postgres' DB
    print("🔧 Connecting to admin DB:", admin_url)  # ✅ NEW: Log admin URL
    if not admin_url:
        raise RuntimeError("❌ DB_ADMIN_URL not set")

    try:
        admin_conn = psycopg2.connect(admin_url)
        admin_conn.autocommit = True
        cursor = admin_conn.cursor()
        # cursor.execute(f"CREATE DATABASE {client_code}")
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (client_code,))  # ✅ NEW: Check if DB exists
        if cursor.fetchone():
            print(f"⚠️ Database '{client_code}' already exists.")  # ✅ NEW: Log existing DB
        else:
            cursor.execute(f"CREATE DATABASE {client_code}")  # ✅ NEW: Create only if not exists
            print(f"✅ Created PostgreSQL database: {client_code}")  # ✅ NEW: Log success
        cursor.close()
        admin_conn.close()
        print(f"✅ Created PostgreSQL database: {client_code}")
    except Exception as e:
        raise RuntimeError(f"❌ Failed to create database {client_code}: {e}")

# ---------- 🔧 ADDED: Connect to client-specific PostgreSQL DB ----------
def get_client_connection(client_code):
    template = os.getenv("DB_URL_TEMPLATE")  # e.g. postgresql://user:pass@host:port/{client}
    if not template:
        raise RuntimeError("❌ DB_URL_TEMPLATE not set")
    
    db_url = template.replace("{client}", client_code)
    try:
        conn = psycopg2.connect(db_url)
        print(f"✅ Connected to client DB: {client_code}")
        return conn
    except Exception as e:
        raise RuntimeError(f"❌ Failed to connect to client DB: {e}")

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

# ✅ FIXED: Wrap table creation inside a proper function
def initialize_database(conn, client_id):
    cursor = conn.cursor()
    placeholder = "%s" if DB_MODE == "cloud" else "?"

    # ✅ FIXED: Create client_keys table first
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_keys (
            client_id TEXT PRIMARY KEY,
            encryption_key TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id {'SERIAL PRIMARY KEY' if DB_MODE == 'cloud' else 'INTEGER PRIMARY KEY AUTOINCREMENT'},
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
    cursor.execute("SELECT encryption_key FROM client_keys WHERE client_id = %s", (client_id,))
    result = cursor.fetchone()
    
    if result:
        encryption_key = result[0]
        print(f"🔐 Existing encryption key found")
    else:
        encryption_key = Fernet.generate_key().decode()
        cursor.execute(
            # f"INSERT INTO client_keys (client_id, encryption_key) VALUES ({placeholder}, {placeholder})",
            "INSERT INTO client_keys (client_id, encryption_key) VALUES (%s, %s)",
            (client_id, encryption_key)
            
        )
        print(f"🆕 New encryption key generated and saved")

    conn.commit()  # ✅ Commit the key insert immediately

    # -------- Insert Default Users --------
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin1",))
    if cursor.fetchone()[0] == 0:
        encrypted_pw = encrypt_password('admin1', encryption_key)  # 🔄 CHANGED
        cursor.execute(
            "INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)",            
            ("admin1", encrypted_pw, "Front Desk", "Admin One")
        )

    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin2",))
    if cursor.fetchone()[0] == 0:
        encrypted_pw = encrypt_password('admin2', encryption_key)  # 🔄 CHANGED
        cursor.execute(
            "INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)",           
            ("admin2", encrypted_pw, "Management", "Admin Two")
        )


    conn.commit()
    conn.close()
    print(f"✅ Database initialized for client: {client_id}")



# ---------- Run only once to initialize ----------
if __name__ == "__main__":
    client_code = input("Enter client code: ")

    if DB_MODE == "cloud":
        create_postgres_database(client_code)
        conn = get_client_connection(client_code)
        initialize_database(conn, client_code)  # ✅ UPDATED: Pass client_id explicitly
    else:
        ghms_folder = find_or_create_ghms_folder()
        db_path = os.path.join(ghms_folder, f"{client_code}.sqlite")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        initialize_database(conn, client_code)  # ✅ UPDATED: Pass client_id explicitly
