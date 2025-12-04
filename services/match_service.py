"""
Match service for student-mentor matching operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection
from models.matches import MentorMatch


class MatchService:
    """Service class for match CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("matches")
    
    def create_match(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new match
        
        Args:
            data: Match data dictionary
            
        Returns:
            dict: Created match with _id
        """
        try:
            # Validate with Pydantic model
            match = MentorMatch(**data)
            
            # Convert to MongoDB document
            match_dict = match.to_mongo()
            if "_id" in match_dict:
                del match_dict["_id"]  # Let MongoDB generate ID
            
            # Insert into database
            result = self.collection.insert_one(match_dict)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating match: {str(e)}")
            return {"error": str(e)}
    
    def list_matches(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List matches with optional filters
        
        Args:
            filters: Optional MongoDB query filters
            
        Returns:
            List of match dictionaries
        """
        try:
            query = filters if filters else {}
            matches_data = self.collection.find(query).sort("created_at", -1)
            return [self._serialize_document(data) for data in matches_data]
            
        except Exception as e:
            print(f"Error listing matches: {str(e)}")
            return []
    
    def get_match_by_id(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a match by ID
        
        Args:
            match_id: Match ID (MongoDB _id)
            
        Returns:
            Match dictionary or None
        """
        try:
            match_data = self.collection.find_one({"_id": ObjectId(match_id)})
            
            if match_data:
                return self._serialize_document(match_data)
            return None
            
        except Exception as e:
            print(f"Error getting match: {str(e)}")
            return None
    
    def update_match(self, match_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a match
        
        Args:
            match_id: Match ID
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated match or error
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(timezone.utc)
            
            result = self.collection.update_one(
                {"_id": ObjectId(match_id)},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return self.get_match_by_id(match_id) or {"success": True}
            
            return {"error": "Match not found or not modified"}
            
        except Exception as e:
            print(f"Error updating match: {str(e)}")
            return {"error": str(e)}
    
    def delete_match(self, match_id: str) -> Dict[str, Any]:
        """
        Delete a match (hard delete)
        
        Args:
            match_id: Match ID
            
        Returns:
            dict: Success status
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(match_id)})
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            
            return {"error": "Match not found"}
            
        except Exception as e:
            print(f"Error deleting match: {str(e)}")
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
    
    def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Alias for get_match_by_id"""
        return self.get_match_by_id(match_id)
    
    def get_all_matches(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all matches (alias for list_matches)
        
        Args:
            status_filter: Filter by status (pending, active, etc.)
            
        Returns:
            List of match dictionaries
        """
        filters = {"status": status_filter} if status_filter else None
        return self.list_matches(filters)
    
    def accept_match(self, match_id: str) -> Dict[str, Any]:
        """
        Accept a pending match
        
        Args:
            match_id: Match ID
            
        Returns:
            dict: Success status or error
        """
        return self.update_match(
            match_id,
            {"status": "active"}
        )
    
    def reject_match(self, match_id: str, reason: str = None) -> Dict[str, Any]:
        """
        Reject a pending match
        
        Args:
            match_id: Match ID
            reason: Optional rejection reason
            
        Returns:
            dict: Success status or error
        """
        updates = {"status": "rejected"}
        if reason:
            updates["rejection_reason"] = reason
        return self.update_match(match_id, updates)
    
    def get_matches_by_student(self, student_id: str) -> List[Dict[str, Any]]:
        """
        Get all matches for a student
        
        Args:
            student_id: Student ID
            
        Returns:
            List of match dictionaries
        """
        return self.list_matches({"student_id": student_id})
    
    def get_matches_by_mentor(self, mentor_id: str) -> List[Dict[str, Any]]:
        """
        Get all matches for a mentor
        
        Args:
            mentor_id: Mentor ID
            
        Returns:
            List of match dictionaries
        """
        return self.list_matches({"mentor_id": mentor_id})
    
    def get_pending_matches(self) -> List[Dict[str, Any]]:
        """
        Get all pending matches
        
        Returns:
            List of pending match dictionaries
        """
        return self.list_matches({"status": "pending"})
    
    def complete_match(self, match_id: str) -> Dict[str, Any]:
        """
        Complete an active match
        
        Args:
            match_id: Match ID
            
        Returns:
            dict: Success status or error
        """
        return self.update_match(match_id, {"status": "completed"})
    
    def get_active_matches(self) -> List[Dict[str, Any]]:
        """
        Get all active matches
        
        Returns:
            List of active match dictionaries
        """
        return self.list_matches({"status": "active"})
