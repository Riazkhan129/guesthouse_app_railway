import os
import sys
import json
from datetime import datetime
from cryptography.fernet import Fernet
from dotenv import load_dotenv  # ✅ NEW: Load .env for local testing
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, APIRouter, Depends, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import psycopg2
import base64
import imghdr


# ✅ Load environment variables from .env (only works locally)
load_dotenv()
DB_MODE = os.getenv("DB_MODE", "local")


# ✅ Define base_path globally
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

sys.path.insert(0, base_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import base64
import imghdr
import psycopg2
from fastapi.responses import JSONResponse
from app.auth import auth_router
from app.db import get_or_create_client_db  # ✅ ADDED

# Local module imports
from app.routes import (
    billing, bookings, checkin_checkout, checkout, guests,
    expenses, users, reports, rooms, invoices, dashboard, performancereport,
    expense_categories, expense_items, roomservice
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
    allow_origins=["*"],
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
app.include_router(performancereport.router)
app.include_router(users.router)
app.include_router(expense_categories.router)
app.include_router(expense_items.router)
app.include_router(roomservice.router)

    
@app.get("/")
def read_root():
    return {"msg": "Welcome to the Guest House Management System API!"}

@app.get("/meta/guesthouse/{client_id}")
def get_guesthouse_name(client_id: str):
    if DB_MODE == "multi-tenant":
        config_url = os.getenv("CONFIG_DB_URL")
        config_conn = psycopg2.connect(config_url)
        config_cursor = config_conn.cursor()
        config_cursor.execute(
            "SELECT client_name, logo FROM client_databases WHERE client_id = %s", (client_id,))
        result = config_cursor.fetchone()
        print("Config_cursor.fetchone = ", result)
        config_conn.close()  # ✅ ADDED: Close config DB connection

        if result:
            guesthouse_name = result[0]
            logo_binary = result[1]
            print("🔍 logo_binary type -- :", type(logo_binary))
            print("🔍 logo_binary repr --:", repr(logo_binary))
            # ✅ ADDED: Encode logo if present
            if logo_binary:
                # ✅ Force correct byte extraction
                if isinstance(logo_binary, memoryview):
                    logo_bytes = logo_binary.tobytes()
                elif isinstance(logo_binary, bytes):
                    logo_bytes = logo_binary
                else:
                    print("❌ Unexpected logo_binary type:", type(logo_binary))
                    logo_bytes = None

                if logo_bytes:
                    print("✅ logo_bytes preview:", logo_bytes[:20])
                    logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
                    mime = imghdr.what(None, h=logo_bytes) or "jpeg"
                    print("🧪 Detected MIME type:", mime)
                    logo_data_url = f"data:image/{mime};base64,{logo_base64}"
                    print("✅ logo_data_url preview:", logo_data_url[:100])
                else:
                    print("⚠️ Could not extract valid image bytes")
            else:
                print("⚠️ No logo found for client")

            return {
                "guesthouse_name": guesthouse_name,
                "logo": logo_data_url
            }

        return JSONResponse(status_code=404, content={"error": "Guesthouse not found"})

    else:
        validate_license(client_id)
        return {
            "guesthouse_name": app.state.guesthouse_name,
            "logo": app.state.logo_data_url
        }

def validate_license(client_code: str):
    try:        
        license_path, key_path, logo_path = get_license_paths(client_code)

        if not os.path.exists(license_path):
            raise FileNotFoundError(f"License file not found for client: {client_code}")
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Key file not found for client: {client_code}")
        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found for client: {client_code}")

        with open(key_path, "rb") as kf:
            key = kf.read()
        cipher = Fernet(key)

        with open(license_path, "rb") as lf:
            encrypted = lf.read()
            
        decrypted = cipher.decrypt(encrypted)
        license_data = json.loads(decrypted.decode())

        app.state.guesthouse_name = license_data.get("guesthouse", "Unknown")
        print("logo_path", logo_path)
        app.state.logo_data_url = encode_logo_file(logo_path)
        
        expiry = license_data.get("expiry")
        if expiry:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            if expiry_date < datetime.today().date():
                raise Exception(f"License expired on {expiry_date}")

        #print(f"✅ License valid for: {app.state.guesthouse_name}")
        #guesthouse_name = app.state.guesthouse_name
        #print(f"✅ GUESTHOUSE_NAME =====", guesthouse_name)
        

        # ✅ ADDED: Initialize DB for this client
        # conn, _ = get_or_create_client_db(client_code)  # ✅ UPDATED
        # conn.close()  # ✅ Now this works correctly

    except Exception as e:
        print("❌ License validation failed:", str(e))
        raise e



# === ✅ Utility: Get license and key paths from package/{client}/ ===
def get_license_paths(client_code):
        client_folder = os.path.join(base_path, "package", client_code)
        print("Client Folder ====", client_folder)
        license_path = os.path.join(client_folder, f"{client_code}.license")
        print("LICENSE_PATH = ", license_path)
        # ✅ Changed from licenses/
        key_path = os.path.join(client_folder, f"{client_code}.key")
        print("KEY_PATH = ", key_path)
              
        logo_path = os.path.join(client_folder, f"{client_code}_logo.png")
        print("LOGO_PATH = ", logo_path)
        
        return license_path, key_path, logo_path

# === Utility: Load and encode logo file ===
def encode_logo_file(logo_path):
    if not os.path.exists(logo_path):
        print(f"⚠️ Logo file not found: {logo_path}")
        return None
    try:
        with open(logo_path, "rb") as lf:
            logo_bytes = lf.read()
        mime = imghdr.what(None, h=logo_bytes) or "jpeg"
        logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
        logo_data_url = f"data:image/{mime};base64,{logo_base64}"
        print("✅ Encoded logo preview:", logo_data_url[:100])
        return logo_data_url
    except Exception as e:
        print(f"❌ Error encoding logo file: {e}")
        return None

# === ✅ NEW: Initialization Endpoint ===
@app.post("/meta/init")
async def initialize_client(request: Request):
    form = await request.form()
    client_id = form.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="Missing client_id")
    try:
        print(f"🚀 Initializing backend for client_id: {client_id}")
        conn, _ = get_or_create_client_db(client_id)
        conn.close()
        return {"status": "initialized", "client_id": client_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")
#-----------------------------------------

# For development or running standalone
if __name__ == "__main__":
    import uvicorn
    import os
    from fastapi_main import app
    print("Starting FastAPI app from executable...")
    uvicorn.run("fastapi_main:app", host="0.0.0.0", port=port, reload=False)

