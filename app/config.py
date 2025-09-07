import os
import sys

def get_base_dir():
    if hasattr(sys, '_MEIPASS'):
        # When running from .exe (PyInstaller)
        return sys._MEIPASS
    return os.path.abspath(os.path.dirname(__file__))

def load_fernet_key():
    key_path = os.path.join(get_base_dir(), "secret.key")
    if not os.path.exists(key_path):
        raise RuntimeError(f"Missing secret.key file at {key_path}")
    with open(key_path, "r") as file:
        return file.read().strip().encode()
