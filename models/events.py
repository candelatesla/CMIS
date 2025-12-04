"""
Event data model
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


def utc_now():
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)


class Event(BaseModel):
    """Event model for CMIS platform"""
    
    id: Optional[str] = Field(None, alias="_id")
    event_id: str = Field(..., description="Unique event identifier")
    name: str
    description: str
    event_type: str = Field(..., description="Type of event (Workshop, Networking, Speaker, Career Fair, etc.)")
    start_datetime: datetime = Field(..., description="Event start time (timezone-aware UTC)")
    end_datetime: datetime = Field(..., description="Event end time (timezone-aware UTC)")
    location: str
    capacity: Optional[int] = Field(None, description="Maximum number of attendees")
    sponsor_tier: Optional[str] = Field(None, description="Sponsor tier (Gold, Silver, Bronze, etc.)")
    
    @field_validator('start_datetime', 'end_datetime', mode='before')
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
                "event_id": "EVT001",
                "name": "AI in Finance Workshop",
                "description": "Learn about AI applications in financial services",
                "event_type": "Workshop",
                "start_datetime": "2024-01-15T18:00:00+00:00",
                "end_datetime": "2024-01-15T20:00:00+00:00",
                "location": "Room 101",
                "capacity": 50,
                "sponsor_tier": "Gold"
            }
        }
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB document"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = self.id
        return data
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Event":
        """Create instance from MongoDB document"""
        if not data:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
