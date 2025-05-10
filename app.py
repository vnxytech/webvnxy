import os
import logging
import json
import uuid
from flask import Flask
from flask_login import LoginManager
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
IMAGES_FILE = f"{DATA_DIR}/images.json"
UPLOAD_DIR = f"{DATA_DIR}/uploads"

# Create data directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create users.json if it doesn't exist with default admin user
if not os.path.exists(USER_FILE):
    # Generate a random access key for admin
    admin_key = str(uuid.uuid4()).replace('-', '')[:16]
    
    default_admin = {
        "id": 1,
        "name": "Admin",
        "access_key": admin_key,
        "role": "admin",
        "active": True,
        "created_at": datetime.now().isoformat()
    }
    
    with open(USER_FILE, 'w') as f:
        json.dump([default_admin], f, indent=4)
    logging.info(f"Created default admin user with access key: {admin_key}")

# Create empty images.json if it doesn't exist
if not os.path.exists(IMAGES_FILE):
    with open(IMAGES_FILE, 'w') as f:
        json.dump([], f, indent=4)

# Import routes after app initialization to avoid circular imports
from routes import *
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
