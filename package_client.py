import os
import json
from cryptography.fernet import Fernet
from datetime import datetime

# === INPUT ===
client_code = input("Enter client code (e.g., GreenStay): ").strip()
guesthouse_name = input("Enter guesthouse name: ").strip()
expiry_date = input("Enter expiry date (YYYY-MM-DD) or leave blank: ").strip()

# === LICENSE METADATA ===
license_data = {
    "guesthouse": guesthouse_name,
    "install_date": datetime.today().strftime("%Y-%m-%d")
}
if expiry_date:
    license_data["expiry"] = expiry_date

# === ENCRYPTION ===
secret_key = Fernet.generate_key()
cipher = Fernet(secret_key)
encrypted_license = cipher.encrypt(json.dumps(license_data).encode())

# === CREATE FOLDERS ===
os.makedirs("licenses", exist_ok=True)
os.makedirs("keys", exist_ok=True)
os.makedirs(f"packages/{client_code}", exist_ok=True)  # ✅ Bundle folder

# === SAVE FILES ===
with open(f"licenses/{client_code}.key", "wb") as f:
    f.write(encrypted_license)

with open(f"keys/{client_code}.key", "wb") as f:
    f.write(secret_key)

with open(f"packages/{client_code}/client_code.txt", "w") as f:
    f.write(client_code)

# === COPY LICENSE + KEY TO PACKAGE ===
with open(f"packages/{client_code}/{client_code}.license", "wb") as f:
    f.write(encrypted_license)

with open(f"packages/{client_code}/{client_code}.key", "wb") as f:
    f.write(secret_key)

# === DONE ===
print(f"\n✅ Package created for '{client_code}' in packages/{client_code}/")
print("Files included:")
print(f"  - client_code.txt")
print(f"  - {client_code}.license")
print(f"  - {client_code}.key")
