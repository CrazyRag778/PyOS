import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open(os.path.join(BASE_DIR, "bin", "register.json")) as f:
    USER_APP_REGISTER = json.load(f) 