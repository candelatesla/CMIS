"""
Case Competition service for database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection
from models.case_competitions import CaseCompetition


class CaseCompService:
    """Service class for case competition CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("case_competitions")
    
    def create_case_competition(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new case competition
        
        Args:
            data: Case competition data dictionary
            
        Returns:
            dict: Created competition with _id
        """
        try:
            # Validate with Pydantic model
            competition = CaseCompetition(**data)
            
            # Convert to MongoDB document
            comp_dict = competition.to_mongo()
            if "_id" in comp_dict:
                del comp_dict["_id"]  # Let MongoDB generate ID
            
            # Insert into database
            result = self.collection.insert_one(comp_dict)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating case competition: {str(e)}")
            return {"error": str(e)}
    
    def list_case_competitions(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List case competitions with optional filters
        
        Args:
            filters: Optional MongoDB query filters
            
        Returns:
            List of case competition dictionaries
        """
        try:
            query = filters if filters else {}
            comps_data = self.collection.find(query).sort("competition_id", 1)
            return [self._serialize_document(data) for data in comps_data]
            
        except Exception as e:
            print(f"Error listing case competitions: {str(e)}")
            return []
    
    def get_case_competition_by_id(self, competition_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a case competition by ID
        
        Args:
            competition_id: Competition ID (either competition_id field or MongoDB _id)
            
        Returns:
            Case competition dictionary or None
        """
        try:
            # Try finding by competition_id field first
            comp_data = self.collection.find_one({"competition_id": competition_id})
            
            # If not found, try by MongoDB _id
            if not comp_data:
                try:
                    comp_data = self.collection.find_one({"_id": ObjectId(competition_id)})
                except:
                    pass
            
            if comp_data:
                return self._serialize_document(comp_data)
            return None
            
        except Exception as e:
            print(f"Error getting case competition: {str(e)}")
            return None
    
    def update_case_competition(self, competition_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a case competition
        
        Args:
            competition_id: Competition ID
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated competition or error
        """
        try:
            # Try updating by competition_id field first
            result = self.collection.update_one(
                {"competition_id": competition_id},
                {"$set": updates}
            )
            
            # If not found, try by MongoDB _id
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(competition_id)},
                        {"$set": updates}
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return self.get_case_competition_by_id(competition_id) or {"success": True}
            
            return {"error": "Competition not found or not modified"}
            
        except Exception as e:
            print(f"Error updating case competition: {str(e)}")
            return {"error": str(e)}
    
    def delete_case_competition(self, competition_id: str) -> Dict[str, Any]:
        """
        Delete a case competition (hard delete)
        
        Args:
            competition_id: Competition ID
            
        Returns:
            dict: Success status
        """
        try:
            # Try deleting by competition_id field first
            result = self.collection.delete_one({"competition_id": competition_id})
            
            # If not found, try by MongoDB _id
            if result.deleted_count == 0:
                try:
                    result = self.collection.delete_one({"_id": ObjectId(competition_id)})
                except:
                    pass
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            
            return {"error": "Competition not found"}
            
        except Exception as e:
            print(f"Error deleting case competition: {str(e)}")
            return {"error": str(e)}
    
    def _serialize_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB document to JSON-serializable dict
        
        Args:
            doc: MongoDB document
            
        Returns:
            JSON-serializable dictionary
        """
        if not doc:
            return None
        
        # Convert ObjectId to string
        if "_id" in doc and isinstance(doc["_id"], ObjectId):
            doc["_id"] = str(doc["_id"])
        
        # Convert datetime objects to ISO format strings
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
        
        return doc
    
    def get_all_competitions(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all case competitions (alias for list_case_competitions)
        
        Args:
            status_filter: Filter by status
            
        Returns:
            List of competition dictionaries
        """
        filters = {"status": status_filter} if status_filter else None
        return self.list_case_competitions(filters)
    
    def get_competitions_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get all competitions for an event
        
        Args:
            event_id: Event ID
            
        Returns:
            List of competition dictionaries
        """
        return self.list_case_competitions({"event_id": event_id})
    
    def register_team(self, competition_id: str, team_data: dict) -> Dict[str, Any]:
        """
        Register a team for a competition
        
        Args:
            competition_id: Competition ID
            team_data: Dictionary with team information
            
        Returns:
            bool: Success status
        """
        try:
            result = self.collection.update_one(
                {"competition_id": competition_id},
                {
                    "$push": {"registered_teams": team_data},
                    "$inc": {"registered_count": 1}
                }
            )
            
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(competition_id)},
                        {
                            "$push": {"registered_teams": team_data},
                            "$inc": {"registered_count": 1}
                        }
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return {"success": True}
            return {"error": "Competition not found"}
            
        except Exception as e:
            print(f"Error registering team: {str(e)}")
            return {"error": str(e)}
    
    def get_active_competitions(self) -> List[Dict[str, Any]]:
        """
        Get active (open) case competitions
        
        Returns:
            List of competition dictionaries
        """
        filters = {
            "status": "open",
            "submission_deadline": {"$gte": datetime.now(timezone.utc)}
        }
        return self.list_case_competitions(filters)
    
    def set_winner(self, competition_id: str, team_id: str) -> Dict[str, Any]:
        """
        Set the winner of a competition
        
        Args:
            competition_id: Competition ID
            team_id: Winning team ID
            
        Returns:
            dict: Success status or error
        """
        return self.update_case_competition(
            competition_id,
            {"winner_team_id": team_id, "status": "completed"}
        )
