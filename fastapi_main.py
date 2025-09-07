import os
import sys
import json
from datetime import datetime
from cryptography.fernet import Fernet



# ✅ Define base_path globally
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

#def get_resource_path(filename):
#    return os.path.join(base_path, filename)

#license_path = get_resource_path("license.key")
#with open(license_path, "rb") as f:
#    encrypted = f.read()

# ✅ Now this works
sys.path.insert(0, base_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# FastAPI imports
from fastapi import FastAPI
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

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Use specific domain in production
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
    return {"guesthouse_name": app.state.guesthouse_name}

# === Utility: Read client code from file ===
def read_client_code():
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
    client_folder = os.path.join(base_path, "package", client_code)
    license_path = os.path.join(client_folder, f"{client_code}.license")  # ✅ Changed from licenses/
    key_path = os.path.join(client_folder, f"{client_code}.key")          # ✅ Changed from keys/
    return license_path, key_path

# === FastAPI Startup Event ===
@app.on_event("startup")
def validate_license():
    try:
        # ✅ Step 1: Get client code
        client_code = read_client_code()

        # ✅ Step 2: Get file paths
        license_path, key_path = get_license_paths(client_code)

        # ✅ Step 3: Check files exist
        if not os.path.exists(license_path):
            raise FileNotFoundError(f"License file not found for client: {client_code}")
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"Key file not found for client: {client_code}")

        # ✅ Step 4: Load key and decrypt license
        with open(key_path, "rb") as kf:
            key = kf.read()
        cipher = Fernet(key)

        with open(license_path, "rb") as lf:
            encrypted = lf.read()
        decrypted = cipher.decrypt(encrypted)
        license_data = json.loads(decrypted.decode())

        # ✅ Step 5: Store guesthouse name
        app.state.guesthouse_name = license_data.get("guesthouse", "Unknown")

        # ✅ Step 6: Check expiry
        expiry = license_data.get("expiry")
        if expiry:
            expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
            if expiry_date < datetime.today().date():
                raise Exception(f"License expired on {expiry_date}")

        print(f"✅ License valid for: {app.state.guesthouse_name}")

    except Exception as e:
        print("❌ License validation failed:", str(e))
        raise e


#-----------------------------------------

# For development or running standalone
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI app from executable...")
    uvicorn.run(app, host="127.0.0.1", port=8000)

