from cryptography.fernet import Fernet
from .config import load_fernet_key

fernet = Fernet(load_fernet_key())

def encrypt_password(password: str) -> str:
    return fernet.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return fernet.decrypt(encrypted_password.encode()).decode()
