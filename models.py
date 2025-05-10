import json
import os
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, id, username, password, role="user", active=True, created_at=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.active = active
        self.created_at = created_at or datetime.now().isoformat()

    @staticmethod
    def get(user_id):
        users = User.get_users()
        for user in users:
            if str(user["id"]) == str(user_id):
                return User(
                    id=user["id"],
                    username=user["username"],
                    password=user["password"],
                    role=user["role"],
                    active=user["active"],
                    created_at=user["created_at"]
                )
        return None

    @staticmethod
    def get_by_username(username):
        users = User.get_users()
        for user in users:
            if user["username"] == username:
                return User(
                    id=user["id"],
                    username=user["username"],
                    password=user["password"],
                    role=user["role"],
                    active=user["active"],
                    created_at=user["created_at"]
                )
        return None

    @staticmethod
    def create(username, password, role="user", active=True):
        users = User.get_users()
        
        # Check if username already exists
        if any(user["username"] == username for user in users):
            return False, "Username already exists"
        
        # Find the next available ID
        next_id = max([user["id"] for user in users], default=0) + 1
        
        new_user = {
            "id": next_id,
            "username": username,
            "password": generate_password_hash(password),
            "role": role,
            "active": active,
            "created_at": datetime.now().isoformat()
        }
        
        users.append(new_user)
        User.save_users(users)
        
        return True, next_id

    @staticmethod
    def update(user_id, data):
        users = User.get_users()
        for i, user in enumerate(users):
            if user["id"] == int(user_id):
                # Update fields that are provided
                for key, value in data.items():
                    if key == 'password' and value:
                        users[i]['password'] = generate_password_hash(value)
                    elif key != 'password':
                        users[i][key] = value
                User.save_users(users)
                return True
        return False

    @staticmethod
    def delete(user_id):
        users = User.get_users()
        for i, user in enumerate(users):
            if user["id"] == int(user_id):
                users.pop(i)
                User.save_users(users)
                return True
        return False

    @staticmethod
    def get_users():
        try:
            with open("data/users.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def save_users(users):
        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=4)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_admin(self):
        return self.role == "admin"

    def is_active(self):
        return self.active

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "active": self.active,
            "created_at": self.created_at
        }


class UserData:
    @staticmethod
    def get_user_uploads(user_id):
        uploads = []
        user_dir = f"data/uploads/{user_id}"
        if not os.path.exists(user_dir):
            return uploads
            
        # List all files in user directory
        for filename in os.listdir(user_dir):
            if filename.endswith(('.json', '.csv')):
                file_path = os.path.join(user_dir, filename)
                file_stats = os.stat(file_path)
                uploads.append({
                    "id": filename,
                    "filename": filename,
                    "size": file_stats.st_size,
                    "uploaded_at": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                    "path": file_path
                })
        
        # Sort by most recent first
        uploads.sort(key=lambda x: x["uploaded_at"], reverse=True)
        return uploads

    @staticmethod
    def get_upload(user_id, file_id):
        file_path = f"data/uploads/{user_id}/{file_id}"
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    return json.load(f)
                elif file_path.endswith('.csv'):
                    content = f.read()
                    return content
        return None

    @staticmethod
    def delete_upload(user_id, file_id):
        file_path = f"data/uploads/{user_id}/{file_id}"
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
