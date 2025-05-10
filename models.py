import json
import os
import uuid
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from datetime import datetime
from flask import url_for

class User(UserMixin):
    def __init__(self, id, name, access_key, role="user", active=True, created_at=None):
        self.id = id
        self.name = name
        self.access_key = access_key
        self.role = role
        # Store the active status in a different variable to avoid conflict with UserMixin
        self.is_account_active = active
        self.created_at = created_at or datetime.now().isoformat()

    @staticmethod
    def get(user_id):
        users = User.get_users()
        for user in users:
            if str(user["id"]) == str(user_id):
                return User(
                    id=user["id"],
                    name=user["name"],
                    access_key=user["access_key"],
                    role=user["role"],
                    active=user.get("active", True),
                    created_at=user["created_at"]
                )
        return None

    @staticmethod
    def get_by_access_key(access_key):
        users = User.get_users()
        for user in users:
            if user["access_key"] == access_key:
                return User(
                    id=user["id"],
                    name=user["name"],
                    access_key=user["access_key"],
                    role=user["role"],
                    active=user.get("active", True),
                    created_at=user["created_at"]
                )
        return None

    @staticmethod
    def create(name, role="user", active=True):
        users = User.get_users()
        
        # Generate unique access key
        access_key = str(uuid.uuid4()).replace('-', '')[:16]
        
        # Find the next available ID
        next_id = max([user["id"] for user in users], default=0) + 1
        
        new_user = {
            "id": next_id,
            "name": name,
            "access_key": access_key,
            "role": role,
            "active": active,
            "created_at": datetime.now().isoformat()
        }
        
        users.append(new_user)
        User.save_users(users)
        
        return True, next_id, access_key

    @staticmethod
    def update(user_id, data):
        users = User.get_users()
        for i, user in enumerate(users):
            if user["id"] == int(user_id):
                # Update fields that are provided
                for key, value in data.items():
                    users[i][key] = value
                User.save_users(users)
                return True
        return False

    @staticmethod
    def regenerate_key(user_id):
        users = User.get_users()
        for i, user in enumerate(users):
            if user["id"] == int(user_id):
                # Generate a new access key
                users[i]["access_key"] = str(uuid.uuid4()).replace('-', '')[:16]
                User.save_users(users)
                return True, users[i]["access_key"]
        return False, None

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
        os.makedirs("data", exist_ok=True)
        with open("data/users.json", "w") as f:
            json.dump(users, f, indent=4)

    def is_admin(self):
        return self.role == "admin"
    
    def get_account_status(self):
        return self.is_account_active

    def get_id(self):
        return str(self.id)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "access_key": self.access_key,
            "role": self.role,
            "active": self.is_account_active,
            "created_at": self.created_at
        }


class Image:
    @staticmethod
    def save_image_data(image_data):
        # Ensure images.json exists
        os.makedirs("data", exist_ok=True)
        try:
            with open("data/images.json", "r") as f:
                images = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            images = []
        
        # Add new image data
        images.append(image_data)
        
        # Save to file
        with open("data/images.json", "w") as f:
            json.dump(images, f, indent=4)
        
        return True

    @staticmethod
    def get_images():
        try:
            with open("data/images.json", "r") as f:
                images = json.load(f)
            
            # Add image URL to each image
            for image in images:
                image["url"] = url_for('get_image', filename=image["filename"])
            
            return images
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def get_image(image_id):
        images = Image.get_images()
        for image in images:
            if str(image["id"]) == str(image_id):
                return image
        return None

    @staticmethod
    def delete_image(image_id):
        try:
            with open("data/images.json", "r") as f:
                images = json.load(f)
            
            for i, image in enumerate(images):
                if str(image["id"]) == str(image_id):
                    # Remove the image file
                    file_path = os.path.join("data/uploads", image["filename"])
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    
                    # Remove the image entry
                    images.pop(i)
                    
                    # Save the updated list
                    with open("data/images.json", "w") as f:
                        json.dump(images, f, indent=4)
                    
                    return True
            
            return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    @staticmethod
    def update_image(image_id, data):
        try:
            with open("data/images.json", "r") as f:
                images = json.load(f)
            
            for i, image in enumerate(images):
                if str(image["id"]) == str(image_id):
                    # Update allowed fields
                    if "title" in data:
                        images[i]["title"] = data["title"]
                    if "description" in data:
                        images[i]["description"] = data["description"]
                    
                    # Save the updated list
                    with open("data/images.json", "w") as f:
                        json.dump(images, f, indent=4)
                    
                    return True
            
            return False
        except (FileNotFoundError, json.JSONDecodeError):
            return False
