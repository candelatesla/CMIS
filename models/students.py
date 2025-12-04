"""
Student data model
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


def utc_now():
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)


class Student(BaseModel):
    """Student model for CMIS platform"""
    
    id: Optional[str] = Field(None, alias="_id")
    student_id: str = Field(..., description="Unique student identifier")
    name: str
    email: EmailStr
    major: str
    grad_year: int = Field(..., description="Expected graduation year")
    interests: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    resume_text: Optional[str] = Field(None, description="Optional resume text, can load from sample_data")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def ensure_timezone_aware(cls, v):
        """Ensure datetime is timezone-aware UTC"""
        if v is None:
            return utc_now()
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "student_id": "STU001",
                "name": "John Doe",
                "email": "john.doe@example.com",
                "major": "Computer Science",
                "grad_year": 2025,
                "skills": ["Python", "Java", "Machine Learning"],
                "interests": ["AI", "Data Science"]
            }
        }
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB document"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = self.id
        return data
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Student":
        """Create instance from MongoDB document"""
        if not data:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
