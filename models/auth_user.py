"""
Authentication User Model
Handles multi-role authentication for Admin, Student, and Mentor users
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class AuthUser(BaseModel):
    """Authentication user model for multi-role access"""
    email: EmailStr
    password_hash: str
    role: str  # "admin", "student", "mentor"
    linked_student_id: Optional[str] = None
    linked_mentor_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
