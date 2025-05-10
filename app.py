import os
import logging
from flask import Flask
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize data storage
DATA_DIR = "data"
USER_FILE = f"{DATA_DIR}/users.json"
UPLOAD_DIR = f"{DATA_DIR}/uploads"

# Create data directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create users.json if it doesn't exist with default admin user
if not os.path.exists(USER_FILE):
    default_admin = {
        "id": 1,
        "username": "admin",
        "password": generate_password_hash("admin123"),
        "role": "admin",
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    
    with open(USER_FILE, 'w') as f:
        json.dump([default_admin], f, indent=4)
    logging.info("Created default admin user: username=admin, password=admin123")

# Import routes after app initialization to avoid circular imports
from routes import *
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
