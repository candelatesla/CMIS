"""
Mentor service for database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection
from models.mentors import Mentor


class MentorService:
    """Service class for mentor CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("mentors")
    
    def create_mentor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new mentor
        
        Args:
            data: Mentor data dictionary
            
        Returns:
            dict: Created mentor with _id
        """
        try:
            # Validate with Pydantic model
            mentor = Mentor(**data)
            
            # Convert to MongoDB document
            mentor_dict = mentor.to_mongo()
            if "_id" in mentor_dict:
                del mentor_dict["_id"]  # Let MongoDB generate ID
            
            # Insert into database
            result = self.collection.insert_one(mentor_dict)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating mentor: {str(e)}")
            return {"error": str(e)}
    
    def list_mentors(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List mentors with optional filters
        
        Args:
            filters: Optional MongoDB query filters
            
        Returns:
            List of mentor dictionaries
        """
        try:
            query = filters if filters else {}
            mentors_data = self.collection.find(query)
            return [self._serialize_document(data) for data in mentors_data]
            
        except Exception as e:
            print(f"Error listing mentors: {str(e)}")
            return []
    
    def get_mentor_by_id(self, mentor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a mentor by ID
        
        Args:
            mentor_id: Mentor ID (either mentor_id field or MongoDB _id)
            
        Returns:
            Mentor dictionary or None
        """
        try:
            # Try finding by mentor_id field first
            mentor_data = self.collection.find_one({"mentor_id": mentor_id})
            
            # If not found, try by MongoDB _id
            if not mentor_data:
                try:
                    mentor_data = self.collection.find_one({"_id": ObjectId(mentor_id)})
                except:
                    pass
            
            if mentor_data:
                return self._serialize_document(mentor_data)
            return None
            
        except Exception as e:
            print(f"Error getting mentor: {str(e)}")
            return None
    
    def get_mentor_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a mentor by email
        
        Args:
            email: Mentor email address
            
        Returns:
            Mentor dictionary or None
        """
        try:
            mentor_data = self.collection.find_one({"email": email})
            
            if mentor_data:
                return self._serialize_document(mentor_data)
            return None
            
        except Exception as e:
            print(f"Error getting mentor by email: {str(e)}")
            return None
    
    def update_mentor(self, mentor_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a mentor
        
        Args:
            mentor_id: Mentor ID
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated mentor or error
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(timezone.utc)
            
            # Try updating by mentor_id field first
            result = self.collection.update_one(
                {"mentor_id": mentor_id},
                {"$set": updates}
            )
            
            # If not found, try by MongoDB _id
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(mentor_id)},
                        {"$set": updates}
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return self.get_mentor_by_id(mentor_id) or {"success": True}
            
            return {"error": "Mentor not found or not modified"}
            
        except Exception as e:
            print(f"Error updating mentor: {str(e)}")
            return {"error": str(e)}
    
    def delete_mentor(self, mentor_id: str) -> Dict[str, Any]:
        """
        Delete a mentor (hard delete)
        
        Args:
            mentor_id: Mentor ID
            
        Returns:
            dict: Success status
        """
        try:
            # Try deleting by mentor_id field first
            result = self.collection.delete_one({"mentor_id": mentor_id})
            
            # If not found, try by MongoDB _id
            if result.deleted_count == 0:
                try:
                    result = self.collection.delete_one({"_id": ObjectId(mentor_id)})
                except:
                    pass
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            
            return {"error": "Mentor not found"}
            
        except Exception as e:
            print(f"Error deleting mentor: {str(e)}")
            return {"error": str(e)}
    
    def get_available_mentors(self) -> List[Dict[str, Any]]:
        """
        Get mentors who are available for new mentees
        
        Returns:
            List of available mentor dictionaries
        """
        try:
            query = {
                "$expr": {"$lt": ["$current_mentees", "$max_mentees"]}
            }
            mentors_data = self.collection.find(query)
            return [self._serialize_document(data) for data in mentors_data]
            
        except Exception as e:
            print(f"Error getting available mentors: {str(e)}")
            return []
    
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
