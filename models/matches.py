"""
MentorMatch data model for student-mentor pairing
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class MentorMatch(BaseModel):
    """MentorMatch model for student-mentor pairing"""
    
    id: Optional[str] = Field(None, alias="_id")
    student_id: str = Field(..., description="Student identifier")
    mentor_id: str = Field(..., description="Mentor identifier")
    match_score: float = Field(..., ge=0.0, le=1.0, description="AI-generated match score (0-1)")
    reason_summary: str = Field(..., description="AI-generated explanation for the match")
    status: str = Field(default="pending", description="Match status: pending, accepted, rejected, active, completed")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "student_id": "STU001",
                "mentor_id": "MEN001",
                "match_score": 0.85,
                "reason_summary": "Strong alignment in AI/ML interests and career goals in technology sector",
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
    def from_mongo(cls, data: Dict[str, Any]) -> "MentorMatch":
        """Create instance from MongoDB document"""
        if not data:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
