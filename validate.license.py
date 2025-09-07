import json
from cryptography.fernet import Fernet
import os
from datetime import datetime

# === INPUT ===
client_id = input("Enter client ID (guesthouse name): ").strip()

# === FILE PATHS ===
license_path = f"licenses/{client_id}.key"
key_path = f"keys/{client_id}.key"

# === CHECK FILES EXIST ===
if not os.path.exists(license_path):
    print(f"❌ License file not found for {client_id}")
    exit()

if not os.path.exists(key_path):
    print(f"❌ Secret key file not found for {client_id}")
    exit()

# === LOAD KEY AND LICENSE ===
with open(key_path, "rb") as kf:
    secret_key = kf.read()

with open(license_path, "rb") as lf:
    encrypted_license = lf.read()

# === DECRYPT LICENSE ===
try:
    cipher = Fernet(secret_key)
    decrypted = cipher.decrypt(encrypted_license)
    license_data = json.loads(decrypted.decode())
except Exception as e:
    print(f"❌ Failed to decrypt license: {e}")
    exit()

# === DISPLAY LICENSE DATA ===
print("🔍 License Data:")
for key, value in license_data.items():
    print(f"  {key}: {value}")

# === CHECK EXPIRY ===
expiry = license_data.get("expiry")
if expiry:
    expiry_date = datetime.strptime(expiry, "%Y-%m-%d").date()
    today = datetime.today().date()
    if today > expiry_date:
        print(f"⚠️ License expired on {expiry_date}")
    else:
        print(f"✅ License is valid until {expiry_date}")
else:
    print("✅ License has no expiry date")

