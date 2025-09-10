# generate_license.py

import os, json
from cryptography.fernet import Fernet

# ✅ Step 1: Prompt user for input
client_id = input("Enter client ID (e.g. demo): ").strip() or "default_client"
guesthouse_name = input("Enter guesthouse name: ").strip() or "Sunrise Inn"
expiry_date = input("Enter expiry date (YYYY-MM-DD) or leave blank: ").strip() or "2025-12-31"

# ✅ Step 2: Create folder
folder = f"package/{client_id}"
os.makedirs(folder, exist_ok=True)

# ✅ Step 3: Generate encryption key
key = Fernet.generate_key()
with open(f"{folder}/{client_id}.key", "wb") as f:
    f.write(key)

# ✅ Step 4: Create license data
license_data = {
    "guesthouse": guesthouse_name,
    "expiry": expiry_date,
    "branding": {
        "logo": "sunrise.png",
        "theme": "light"
    },
    "features": ["billing", "reports", "multi-room"]
}

# ✅ Step 5: Encrypt license
cipher = Fernet(key)
encrypted = cipher.encrypt(json.dumps(license_data).encode())

with open(f"{folder}/{client_id}.license", "wb") as f:
    f.write(encrypted)

# ✅ Step 6: Save client_code.txt
with open(f"{folder}/client_code.txt", "w") as f:
    f.write(client_id)

print(f"✅ License and key created for {client_id}")
print(f"📁 Files saved in: {folder}")
print(f"🔐 License expiry: {expiry_date}")
