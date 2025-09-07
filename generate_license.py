import json
from cryptography.fernet import Fernet
import os

# === CONFIGURATION ===
#FERNET_KEY = b'twL7Pat5yGTWlYACW9nTn6wxaEvtENeNDCXGJApERq4='  # Same key as your FastAPI app
#OUTPUT_PATH = "license.key"  # You can change this to "licenses/LodgeControl.key" etc.

# ✅ Prompt user for client info
guesthouse_name = input("Enter guesthouse name: ").strip()
expiry_date = input("Enter expiry date (YYYY-MM-DD) or leave blank: ").strip()

# ✅ NEW: Generate unique key per client
secret_key = Fernet.generate_key()
cipher = Fernet(secret_key)

# ✅ Build license data
license_data = {
    "guesthouse": guesthouse_name,
}

if expiry_date:
    license_data["expiry"] = expiry_date

# ✅ Encrypt license
encrypted = cipher.encrypt(json.dumps(license_data).encode())

# ✅ NEW: Create folders if missing
os.makedirs("licenses", exist_ok=True)
os.makedirs("keys", exist_ok=True)

# ✅ NEW: Save license and key per client
with open(f"licenses/{guesthouse_name}.key", "wb") as f:
    f.write(encrypted)

with open(f"keys/{guesthouse_name}.key", "wb") as f:
    f.write(secret_key)

# ✅ Confirmation messages
print(f"✅ License saved to licenses/{guesthouse_name}.key")
print(f"🔐 Secret key saved to keys/{guesthouse_name}.key")

# python generate_license.py

