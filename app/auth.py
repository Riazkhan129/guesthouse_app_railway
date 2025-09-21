# auth.py

from fastapi import APIRouter, Depends, HTTPException, Form, status
from fastapi.security import OAuth2PasswordBearer
from cryptography.fernet import Fernet
from .crud import get_encryption_key
from .db import get_or_create_client_db  # ✅ ADDED: Single entry point for DB setup
import os

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@auth_router.post("/token")
def login(
    username: str = Form(...),
    password: str = Form(...),
    client_id: str = Form(...)
):
    print("Login request received")
    print("Username:", username)
    print("Password:", password)
    print("Client ID:", client_id)

    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")    
    try:
        conn, _ = get_or_create_client_db(client_id) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    cursor = conn.cursor()
    placeholder = "%s" if os.getenv("DB_MODE") == "multi-tenant" else "?"
    try:
        query = f"SELECT username, password, role FROM users WHERE username = {placeholder}"
        cursor.execute(query, (username,))
        user = cursor.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Query failed: {e}")

    if user:
        db_username, db_encrypted_password, db_role = user
        key = get_encryption_key(client_id)
        if not key:
            raise HTTPException(status_code=500, detail="Encryption key not found")

        fernet = Fernet(key.encode())
        try:
            decrypted_password = fernet.decrypt(db_encrypted_password.encode()).decode()
            if decrypted_password == password:
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

@auth_router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token.endswith("_token"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = token.replace("_token", "")
    return {"username": username}
