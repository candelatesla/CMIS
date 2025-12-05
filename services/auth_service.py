"""
Authentication Service
Handles user authentication and password management for multi-role system
"""
import hashlib
from datetime import datetime
from typing import Optional, Dict
from db import get_database


class AuthService:
    """Service for managing authentication users"""
    
    def __init__(self):
        self.db = get_database()
        self.collection = self.db["auth_users"]
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == password_hash
    
    def create_user(
        self, 
        email: str, 
        password: str, 
        role: str,
        linked_student_id: Optional[str] = None,
        linked_mentor_id: Optional[str] = None
    ) -> Dict:
        """Create a new authentication user"""
        try:
            # Check if user already exists
            existing = self.get_user(email, role)
            if existing:
                return {"error": "User with this email and role already exists"}
            
            # Create user document
            user_data = {
                "email": email,
                "password_hash": self.hash_password(password),
                "role": role,
                "linked_student_id": linked_student_id,
                "linked_mentor_id": linked_mentor_id,
                "created_at": datetime.utcnow()
            }
            
            result = self.collection.insert_one(user_data)
            user_data["_id"] = str(result.inserted_id)
            
            return {"success": True, "user_id": str(result.inserted_id)}
        
        except Exception as e:
            return {"error": str(e)}
    
    def get_user(self, email: str, role: str) -> Optional[Dict]:
        """Get user by email and role"""
        try:
            user = self.collection.find_one({"email": email, "role": role})
            if user:
                user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None
    
    def authenticate_user(self, email: str, password: str, role: str) -> Optional[Dict]:
        """Authenticate user with email, password, and role"""
        try:
            user = self.get_user(email, role)
            if not user:
                return None
            
            if self.verify_password(password, user["password_hash"]):
                return user
            
            return None
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None
