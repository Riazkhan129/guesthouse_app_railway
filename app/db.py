# db.py

import os
import sqlite3
import psycopg2
import string
# from contextlib import contextmanager
from cryptography.fernet import Fernet
# import sys


# ---------- 🧠 Environment Mode Detection ----------
DB_MODE = os.getenv("DB_MODE", "local")  # ✅ 'local' or 'multi-tenant'

print("DB_MODE = ", DB_MODE)

# ---------- Get Available Drives ----------
def get_available_drives():
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

    # ✅ ADDED: Fallback for Linux environments
    if not drives:
        drives.append(os.getcwd())
    return drives

# ---------- Create or Find ghms Folder ----------
def find_or_create_ghms_folder():
    drives = get_available_drives()
    #if not result:
    #    raise RuntimeError(f"❌ No DB URL found for client '{client_id}'")  # ✅ Error if missing
    for drive in drives:
        ghms_path = os.path.join(drive, "ghms")
        try:
            os.makedirs(ghms_path, exist_ok=True)
            return ghms_path
        except Exception as e:
            print(f"❌ Could not access {ghms_path}: {e}")
    
    raise RuntimeError("❌ Could not create ghms folder on any available drive.")


# ✅ ADDED: Unified DB setup for local and multi-tenant


#----------------------
def get_or_create_client_db(client_id):
    try:
        if DB_MODE == "multi-tenant":
            config_url = os.getenv("CONFIG_DB_URL")
            config_conn = psycopg2.connect(config_url)
            config_cursor = config_conn.cursor()
            config_cursor.execute("SELECT db_url, client_name FROM client_databases WHERE client_id = %s", (client_id,))
            result = config_cursor.fetchone()
            print("Config_cursor.fetchone = ", result)
            config_conn.close()  # ✅ ADDED: Close config DB connection
            
            
            if not result:
                raise RuntimeError(f"❌ No DB URL found for client '{client_id}'")  # ✅ ADDED: Error if missing
            # print("In get_or_create_client_db - fb_url = ", db_url)
            
            db_url = result[0]  # ✅ ADDED: Extract actual DB URL
            print("✅ Retrieved DB URL from config table:", db_url)
            
            conn = psycopg2.connect(db_url)
            conn.autocommit = True
            placeholder = "%s"  # ✅ PostgreSQL placeholder
            print(f"✅ Connected to PostgreSQL DB for client: {client_id}")
            print(f"🔧 DB_MODE: {DB_MODE}")
            print(f"🔧 Initializing DB for client: {client_id}")
        else:
            ghms_folder = find_or_create_ghms_folder()
            db_path = os.path.join(ghms_folder, "smarthost.sqlite")
            # db_path = os.path.join(ghms_folder, f"{client_id}.sqlite")
            if not os.path.exists(db_path):
                print(f"⚠️ Local DB for client '{client_id}' not found. Creating...")
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            placeholder = "?"  # ✅ SQLite placeholder
            print(f"✅ Connected to SQLite DB for client: {client_id}")

        initialize_database(conn if DB_MODE == "multi-tenant" else db_path, client_id)  # ✅ ADDED: Pass client_id
        return conn, placeholder  # ✅ Return both values
    except Exception as e:
        raise RuntimeError(f"❌ Failed to prepare DB for client '{client_id}': {e}")
# ---------- FastAPI Dependency ----------
#def get_db():
#    db = get_connection()
#    try:
#        yield db
#    finally:
#        db.close()

# ---------- Encrypt password ----------
def encrypt_password(password: str, key: str) -> str:
    fernet = Fernet(key.encode())
    return fernet.encrypt(password.encode()).decode()

# ---------- Create Tables & Insert Default Data ----------
def initialize_database(db_path_or_conn, client_id):
    if DB_MODE == "multi-tenant":
        conn = db_path_or_conn  # 🔄 UPDATED: PostgreSQL connection
        placeholder = "%s"
    else:
        db_path = db_path_or_conn
        if not os.path.exists(db_path):
            print(" DB file not found. Creating a new one...")
        else:
            print(" DB file found.")
        conn = sqlite3.connect(db_path)
        placeholder = "?"

    cursor = conn.cursor()

    # ✅ FIXED: Create client_keys table first
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS client_keys (
            client_id TEXT PRIMARY KEY,
            encryption_key TEXT NOT NULL
        )
    """) 

    print("✅ 'client_keys' table creation executed")  # ✅ ADDED: Debug log

    user_id_column = "user_id SERIAL PRIMARY KEY" if DB_MODE == "multi-tenant" else "user_id INTEGER PRIMARY KEY AUTOINCREMENT"    
    
    sql_users = f"""
        CREATE TABLE IF NOT EXISTS users (
            {user_id_column},
            name TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """

    cursor.execute(sql_users)

    print("✅ 'users' table creation executed")  # ✅ ADDED: Debug log

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

    print("✅ 'guests' table creation executed")  # ✅ ADDED: Debug log

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_number TEXT NOT NULL,
            type TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT NOT NULL,
            notes TEXT
        )
    """)

    print("✅ 'rooms' table creation executed")  # ✅ ADDED: Debug log

    booking_id_column = "booking_id SERIAL PRIMARY KEY" if DB_MODE == "multi-tenant" else "booking_id INTEGER PRIMARY KEY AUTOINCREMENT"
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS bookings (
            {booking_id_column},
            nic_passport_number TEXT,
            room_number TEXT,
            room_type TEXT,
            rooam_rate INTEGER
            checkin_date TEXT,
            checkout_date TEXT,
            status TEXT,
            notes TEXT,
            actual_checkin_time TEXT,
            companions INTEGER,
            advance_payment REAL,
            actual_checkout_time TEXT,
            total_payment REAL,
            invoice_id INTEGER,
            FOREIGN KEY (nic_passport_number) REFERENCES guests(nic_passport_number)
        )
    """)

    print("✅ 'booking' table creation executed")  # ✅ ADDED: Debug log

    id_column = "expense_id SERIAL PRIMARY KEY" if DB_MODE == "multi-tenant" else "expeense_id INTEGER PRIMARY KEY AUTOINCREMENT"
    
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS expenses (
            {id_column},
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT,
            timestamp TEXT,
            date TEXT
        )
    """)

    print("✅ 'expenses' table creation executed")  # ✅ ADDED: Debug log


    invoice_id_column = (
        "invoice_id SERIAL PRIMARY KEY"
        if DB_MODE == "multi-tenant"
        else "invoice_id INTEGER PRIMARY KEY AUTOINCREMENT")
        
    query = f"""
    CREATE TABLE IF NOT EXISTS invoices (
        {invoice_id_column},
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
    """

    cursor.execute(query)

    print("✅ 'invoices' table creation executed")  # ✅ ADDED: Debug log

# ---------- Encryption Key ----------
    
    if DB_MODE == "multi-tenant":
        cursor.execute("SELECT encryption_key FROM client_keys WHERE client_id = %s", (client_id,))
    else:
        cursor.execute("SELECT encryption_key FROM client_keys WHERE client_id = ?", (client_id,))
    result = cursor.fetchone()
    
    if result:
        encryption_key = result[0]
        print(f"🔐 Existing encryption key found")
    else:
        encryption_key = Fernet.generate_key().decode()
        if DB_MODE == "multi-tenant":
            cursor.execute("INSERT INTO client_keys (client_id, encryption_key) VALUES (%s, %s)", (client_id, encryption_key))
        else:
            cursor.execute("INSERT INTO client_keys (client_id, encryption_key) VALUES (?, ?)", (client_id, encryption_key))
        print("🆕 New encryption key generated and saved")

    conn.commit()  # ✅ Commit the key insert immediately

# -------- Insert Default Users --------
        
    if DB_MODE == "multi-tenant":
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin1",))
    else:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin1",))
    if cursor.fetchone()[0] == 0:
        encrypted_pw = encrypt_password("admin1", encryption_key)
        if DB_MODE == "multi-tenant":
            cursor.execute("INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)",
                           ("admin1", encrypted_pw, "Front Desk", "Admin One"))
        else:
            cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                           ("admin1", encrypted_pw, "Front Desk", "Admin One"))

    if DB_MODE == "multi-tenant":
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", ("admin2",))
    else:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin2",))
    if cursor.fetchone()[0] == 0:
        encrypted_pw = encrypt_password("admin2", encryption_key)
        print ("In DB.PY encryption key ====", encryption_key)
        if DB_MODE == "multi-tenant":
            cursor.execute("INSERT INTO users (username, password, role, name) VALUES (%s, %s, %s, %s)",
                           ("admin2", encrypted_pw, "Management", "Admin Two"))
        else:
            cursor.execute("INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)",
                           ("admin2", encrypted_pw, "Management", "Admin Two"))

    conn.commit()
    print(f"✅ Database initialized for client: {client_id}")
    

# ---------- Run only once to initialize ----------
if __name__ == "__main__":
    if DB_MODE == "multi-tenant":
        # conn = get_connection()
        conn = get_or_create_client_db(client_id)
        initialize_database(conn)  # ✅ ADDED: multi-tenant mode uses connection
    else:
        ghms_folder = find_or_create_ghms_folder()
        db_path = os.path.join(ghms_folder, "guesthouse.sqlite")
        initialize_database(db_path)  # ✅ Local mode uses file path
