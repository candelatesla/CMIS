"""
Case Competition data model
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CaseCompetition(BaseModel):
    """Case Competition model for CMIS platform"""
    
    id: Optional[str] = Field(None, alias="_id")
    competition_id: str = Field(..., description="Unique competition identifier")
    name: str
    description: str
    event_id: str = Field(..., description="Associated event ID")
    judges: List[str] = Field(default_factory=list, description="List of judge names")
    team_size_min: int = Field(default=1, description="Minimum team size")
    team_size_max: int = Field(default=4, description="Maximum team size")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "competition_id": "COMP001",
                "name": "FinTech Innovation Challenge",
                "description": "Develop a solution for financial inclusion",
                "event_id": "EVT001",
                "judges": ["Dr. Smith", "Prof. Johnson"],
                "team_size_min": 2,
                "team_size_max": 4
            }
        }
    
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB document"""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if self.id:
            data["_id"] = self.id
        return data
    
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "CaseCompetition":
        """Create instance from MongoDB document"""
        if not data:
            return None
        if "_id" in data:
            data["_id"] = str(data["_id"])
        return cls(**data)
