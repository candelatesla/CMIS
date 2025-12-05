"""
EmailLog data model for tracking email communications
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator


def utc_now():
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)


class EmailLog(BaseModel):
    """EmailLog model for tracking sent emails"""
    
    id: Optional[str] = Field(None, alias="_id")
    recipient_email: EmailStr = Field(..., description="Email address of recipient")
    recipient_role: str = Field(..., description="Role of recipient: student, mentor, admin")
    subject: str
    body: str
    related_match_id: Optional[str] = Field(None, description="Related mentor match ID if applicable")
    planned_send_time: datetime = Field(default_factory=utc_now, description="When email is planned to be sent")
    actual_send_time: Optional[datetime] = Field(None, description="When email was actually sent")
    status: str = Field(default="pending", description="Email status: scheduled, sent, failed")
    error_message: Optional[str] = Field(None, description="Error message if sending failed")
    created_at: datetime = Field(default_factory=utc_now, description="When record was created")
    
    @field_validator('planned_send_time', 'actual_send_time', 'created_at', mode='before')
    @classmethod
    def ensure_timezone_aware(cls, v):
        """Ensure datetime is timezone-aware UTC"""
        if v is None:
            return None
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
                "recipient_email": "student@example.com",
                "recipient_role": "student",
                "subject": "New Mentor Match Available",
                "body": "You have been matched with a mentor...",
                "related_match_id": "MATCH001",
                "status": "pending"
            }
        }
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB document"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = self.id
        return data
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "EmailLog":
        """Create instance from MongoDB document"""
        if not data:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
