import os
import sys
import json
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv  # ✅ NEW: Load .env for local testing
from fastapi.middleware.cors import CORSMiddleware
# ✅ ADDED: Import DB initializer
from app.db import get_or_create_client_db  # ✅ ADDED: Initialize DB per client



# ✅ Load environment variables from .env (only works locally)
load_dotenv()


# ✅ Define base_path globally
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

sys.path.insert(0, base_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# FastAPI imports
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from app.auth import auth_router
from app.db import initialize_database
from app.crud import get_all_bookings  # Optional: only if you use it somewhere

# Local module imports
from app.routes import (
    billing, bookings, checkin_checkout, checkout, guests,
    expenses, users, reports, rooms, invoices, dashboard
)

# Initialize FastAPI app
app = FastAPI(title="Guest House Management System")
port = int(os.getenv("PORT", 8000))

# ✅ Allow your frontend domain
origins = [
    "https://lodgecontrol.up.railway.app",  # ✅ Your deployed frontend
    "http://localhost:3000",                # ✅ For local development
]

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth_router)
app.include_router(bookings.router)
app.include_router(checkin_checkout.router)
app.include_router(checkout.router)
app.include_router(guests.router)
app.include_router(billing.router)
app.include_router(invoices.router)
app.include_router(dashboard.router)
app.include_router(rooms.router)
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(users.router)

    
@app.get("/")
def read_root():
    return {"msg": "Welcome to the Guest House Management System API!"}

@app.get("/meta/guesthouse")
def get_guesthouse_name():
    guesthouse_name = os.getenv("CLIENT_NAME")
    print("Guest Name from FastAPI ", guesthouse_name)
    return {"guesthouse_name": app.state.guesthouse_name}

# === Utility: Read client code from file ===
def read_client_code():
    env_client_id = os.getenv("CLIENT_ID")
    if env_client_id:
        print(f"✅ Using CLIENT_ID from environment: {env_client_id}")
        return env_client_id

    # Fallback to reading from client_code.txt
    try:
        package_dir = os.path.join(base_path, "package")
        for folder in os.listdir(package_dir):
            client_code_path = os.path.join(package_dir, folder, "client_code.txt")
            if os.path.exists(client_code_path):
                with open(client_code_path, "r") as f:
                    return f.read().strip()
        print("❌ No client_code.txt found in package folders.")
        return "default_client"
    except Exception as e:
        print(f"❌ Error reading client_code.txt: {e}")
        return "default_client"

# === ✅ Utility: Get license and key paths from package/{client}/ ===
def get_license_paths(client_code):
    # ✅ Use LICENSE_PATH from env if available
    env_license_path = os.getenv("LICENSE_PATH")
    if env_license_path:
        license_path = env_license_path
        key_path = env_license_path.replace(".license", ".key")
        print(f"✅ Using LICENSE_PATH from environment: {license_path}")
    else:
        client_folder = os.path.join(base_path, "package", client_code)
        license_path = os.path.join(client_folder, f"{client_code}.license")  # ✅ Changed from licenses/
        key_path = os.path.join(client_folder, f"{client_code}.key")          # ✅ Changed from keys/
    return license_path, key_path

# === ✅ NEW: License Check Endpoint ===
@app.get("/meta/license-check")
def license_check():
    try:
        client_code = read_client_code()
        license_path, key_path = get_license_paths(client_code)

        license_exists = os.path.exists(license_path)
        key_exists = os.path.exists(key_path)

        if not license_exists or not key_exists:
            raise FileNotFoundError("License or key file missing")

        with open(key_path, "rb") as kf:
            key = kf.read()
        cipher = Fernet(key)

        with open(license_path, "rb") as lf:
            encrypted = lf.read()
        decrypted = cipher.decrypt(encrypted)
        license_data = json.loads(decrypted.decode())

        expiry = license_data.get("expiry")
        guesthouse = license_data.get("guesthouse", "Unknown")
        if expiry:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            expired = expiry_date < datetime.today().date()
        else:
            expired = False

        return {
            "client_id": client_code,
            "guesthouse": guesthouse,
            "license_expiry": expiry,
            "license_expired": expired,
            "license_path": license_path,
            "key_path": key_path,
            "license_valid": not expired
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"License check failed: {str(e)}")
# === FastAPI Startup Event ===
@app.on_event("startup")
def validate_license():
    try:        
        client_code = read_client_code()
        license_path, key_path = get_license_paths(client_code)

        if not os.path.exists(license_path):
            raise FileNotFoundError(f"License file not found for client: {client_code}")
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Key file not found for client: {client_code}")

        with open(key_path, "rb") as kf:
            key = kf.read()
        cipher = Fernet(key)

        with open(license_path, "rb") as lf:
            encrypted = lf.read()
        decrypted = cipher.decrypt(encrypted)
        license_data = json.loads(decrypted.decode())

        app.state.guesthouse_name = license_data.get("guesthouse", "Unknown")

        expiry = license_data.get("expiry")
        if expiry:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            if expiry_date < datetime.today().date():
                raise Exception(f"License expired on {expiry_date}")

        print(f"✅ License valid for: {app.state.guesthouse_name}")

        # ✅ ADDED: Initialize DB for this client
        conn, _ = get_or_create_client_db(client_code)  # ✅ UPDATED
        conn.close()  # ✅ Now this works correctly

    except Exception as e:
        print("❌ License validation failed:", str(e))
        raise e


#-----------------------------------------

# For development or running standalone
if __name__ == "__main__":
    import uvicorn
    import os
    print("Starting FastAPI app from executable...")
    uvicorn.run("fastapi_main:app", host="0.0.0.0", port=port, reload=True)

