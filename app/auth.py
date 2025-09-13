from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .crud import verify_password, get_encryption_key
from .models import Client_keysBase
# from .db import get_connection, get_db
# 🔧 ADDED: Import full DB logic
from .db import (
    DB_MODE,
    create_postgres_database,
    get_client_connection,
    find_or_create_ghms_folder,
    initialize_database
)
import sqlite3
import psycopg2
import os
from cryptography.fernet import Fernet

auth_router = APIRouter()

# For protected endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# client_id = "ngh"

# --------- Login: Verify Encrypted Password ---------

@auth_router.post("/token")
def login(
    username: str = Form(...),  # ✅ NEW: Accept username from form
    password: str = Form(...),  # ✅ NEW: Accept password from form
    client_id: str = Form(...),  # ✅ NEW: Accept client_id from form
    # db: sqlite3.Connection = Depends(get_db)
    
):
    print("Login request received")
    print("Username:", username)
    print("Password:", password)
    print("Client ID:", client_id)

    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")

    # ---------- 🔧 ADDED: Create or connect to client DB ----------
    try:
        if DB_MODE == "cloud":
            try:
                create_postgres_database(client_id)
            except Exception as e:
                print(f"⚠️ Database may already exist: {e}")
            conn = get_client_connection(client_id)
        else:
            ghms_folder = find_or_create_ghms_folder()
            db_path = os.path.join(ghms_folder, f"{client_id}.sqlite")
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA foreign_keys = ON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to connect to client DB: {e}")

     # ---------- 🔧 ADDED: Initialize DB if needed ----------
    try:
        initialize_database(conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Failed to initialize DB: {e}")
    # cursor = db.cursor()
    cursor = conn.cursor()

    try:
        placeholder = "%s" if DB_MODE == "cloud" else "?"
        query = f"SELECT username, password, role FROM users WHERE username = {placeholder}"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Query failed: {e}")

    print("User fetched from DB:", user)

    # -----------
    #user = cursor.execute(
    #    "SELECT username, password, role FROM users WHERE username = ?",  
    #    (username,)
    #).fetchone()

    print("User fetched from DB:", user)
    
    if user:
        db_username, db_encrypted_password, db_role = user  # ✅ UPDATED: Unpack client_id

        # ✅ NEW: Fetch encryption key for this client
        key = get_encryption_key(client_id)
        
        if not key:
            raise HTTPException(status_code=500, detail="Encryption key not found")

        fernet = Fernet(key.encode())  # ✅ NEW: Create Fernet instance with client-specific key

        try:
            decrypted_password = fernet.decrypt(db_encrypted_password.encode()).decode()
            print("decrypted_password = ", decrypted_password)
            print("password = ", password)
            
            if decrypted_password == password:
                # Dummy token (can replace with JWT later)
                return {
                    "access_token": f"{db_username}_token",
                    "token_type": "bearer",
                    "username": db_username,
                    "role": db_role,
                    "client_id": client_id
                }
        except Exception as e:
            print("Decryption failed:", e)

    raise HTTPException(status_code=401, detail="Invalid username or password")


# --------- Get Current User (Token Based) ---------
@auth_router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token.endswith("_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract username (e.g., admin_token → admin)
    username = token.replace("_token", "")

    return {"username": username}


