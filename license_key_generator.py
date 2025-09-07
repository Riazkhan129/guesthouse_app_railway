from fastapi import FastAPI, Query
from cryptography.fernet import Fernet
import json
import os

app = FastAPI()

@app.get("/generate-license")
def generate_license(
    client_id: str = Query(...),        # ✅ NEW: Accept client name
    expiry: str = Query(None)           # ✅ NEW: Optional expiry date
):
    # ✅ NEW: Generate unique key per client
    secret_key = Fernet.generate_key()
    cipher = Fernet(secret_key)

    # ✅ NEW: License metadata per client
    license_data = {
        "guesthouse": client_id,
        "install_date": "2025-09-02",   # You can make this dynamic
        "expiry": expiry
    }

    # ✅ Encrypt license data
    encrypted = cipher.encrypt(json.dumps(license_data).encode())

    # ✅ NEW: Create folders if missing
    os.makedirs("licenses", exist_ok=True)
    os.makedirs("keys", exist_ok=True)

    # ✅ NEW: Save license and key per client
    with open(f"licenses/{client_id}.key", "wb") as f:
        f.write(encrypted)

    with open(f"keys/{client_id}.key", "wb") as f:
        f.write(secret_key)

    return {
        "message": f"License saved for {client_id}",
        "client_id": client_id
    }
