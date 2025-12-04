"""
Mentor data model
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


def utc_now():
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)


class Mentor(BaseModel):
    """Mentor model for CMIS platform"""
    
    id: Optional[str] = Field(None, alias="_id")
    mentor_id: str = Field(..., description="Unique mentor identifier")
    name: str
    email: EmailStr
    company: str
    job_title: str
    industry: str
    expertise_areas: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    max_mentees: int = Field(default=3, description="Maximum number of mentees")
    current_mentees: int = Field(default=0, description="Current number of active mentees")
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
                "mentor_id": "MEN001",
                "name": "Jane Smith",
                "email": "jane.smith@company.com",
                "company": "Tech Corp",
                "job_title": "Senior Software Engineer",
                "industry": "Technology",
                "expertise_areas": ["Software Development", "Cloud Architecture"],
                "interests": ["Mentoring", "AI"],
                "max_mentees": 3,
                "current_mentees": 1
            }
        }
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB document"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = self.id
        return data
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Mentor":
        """Create instance from MongoDB document"""
        if not data:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
