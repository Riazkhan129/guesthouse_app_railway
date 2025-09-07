import os
from datetime import datetime, timedelta

TRIAL_FILE = "trial.txt"
TRIAL_DAYS = 30

def check_trial():
    if not os.path.exists(TRIAL_FILE):
        with open(TRIAL_FILE, "w") as f:
            start_date = datetime.now()
            f.write(start_date.isoformat())
        return True

    with open(TRIAL_FILE, "r") as f:
        start_date = datetime.fromisoformat(f.read().strip())

    if datetime.now() - start_date > timedelta(days=TRIAL_DAYS):
        print("❌ Trial expired. Please contact support.")
        return False
    return True
