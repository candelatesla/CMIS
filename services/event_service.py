"""
Event service for database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection
from models.events import Event


class EventService:
    """Service class for event CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("events")
    
    def create_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new event
        
        Args:
            data: Event data dictionary
            
        Returns:
            dict: Created event with _id
        """
        try:
            # Validate with Pydantic model
            event = Event(**data)
            
            # Convert to MongoDB document
            event_dict = event.to_mongo()
            if "_id" in event_dict:
                del event_dict["_id"]  # Let MongoDB generate ID
            
            # Insert into database
            result = self.collection.insert_one(event_dict)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            return {"error": str(e)}
    
    def list_events(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List events with optional filters
        
        Args:
            filters: Optional MongoDB query filters
            
        Returns:
            List of event dictionaries
        """
        try:
            query = filters if filters else {}
            events_data = self.collection.find(query).sort("start_datetime", 1)
            return [self._serialize_document(data) for data in events_data]
            
        except Exception as e:
            print(f"Error listing events: {str(e)}")
            return []
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an event by ID
        
        Args:
            event_id: Event ID (either event_id field or MongoDB _id)
            
        Returns:
            Event dictionary or None
        """
        try:
            # Try finding by event_id field first
            event_data = self.collection.find_one({"event_id": event_id})
            
            # If not found, try by MongoDB _id
            if not event_data:
                try:
                    event_data = self.collection.find_one({"_id": ObjectId(event_id)})
                except:
                    pass
            
            if event_data:
                return self._serialize_document(event_data)
            return None
            
        except Exception as e:
            print(f"Error getting event: {str(e)}")
            return None
    
    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an event
        
        Args:
            event_id: Event ID
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated event or error
        """
        try:
            # Try updating by event_id field first
            result = self.collection.update_one(
                {"event_id": event_id},
                {"$set": updates}
            )
            
            # If not found, try by MongoDB _id
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(event_id)},
                        {"$set": updates}
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return self.get_event_by_id(event_id) or {"success": True}
            
            return {"error": "Event not found or not modified"}
            
        except Exception as e:
            print(f"Error updating event: {str(e)}")
            return {"error": str(e)}
    
    def delete_event(self, event_id: str) -> Dict[str, Any]:
        """
        Delete an event (hard delete)
        
        Args:
            event_id: Event ID
            
        Returns:
            dict: Success status
        """
        try:
            # Try deleting by event_id field first
            result = self.collection.delete_one({"event_id": event_id})
            
            # If not found, try by MongoDB _id
            if result.deleted_count == 0:
                try:
                    result = self.collection.delete_one({"_id": ObjectId(event_id)})
                except:
                    pass
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            
            return {"error": "Event not found"}
            
        except Exception as e:
            print(f"Error deleting event: {str(e)}")
            return {"error": str(e)}
    
    def get_upcoming_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            query = {
                "start_datetime": {"$gte": datetime.now(timezone.utc)}
            }
            events_data = self.collection.find(query).sort("start_datetime", 1).limit(limit)
            return [self._serialize_document(data) for data in events_data]
            
        except Exception as e:
            print(f"Error getting upcoming events: {str(e)}")
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
    
    def get_upcoming_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        try:
            query = {
                "start_datetime": {"$gte": datetime.now(timezone.utc).isoformat()}
            }
            events_data = self.collection.find(query).sort("start_datetime", 1).limit(limit)
            return [self._serialize_document(data) for data in events_data]
            
        except Exception as e:
            print(f"Error getting upcoming events: {str(e)}")
            return []
    
    def register_student(self, event_id: str, student_id: str) -> Dict[str, Any]:
        """
        Register a student for an event
        
        Args:
            event_id: Event ID
            student_id: Student ID
            
        Returns:
            dict: Success status or error
        """
        try:
            result = self.collection.update_one(
                {"event_id": event_id},
                {
                    "$addToSet": {"registered_students": student_id},
                    "$inc": {"registered_count": 1}
                }
            )
            
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(event_id)},
                        {
                            "$addToSet": {"registered_students": student_id},
                            "$inc": {"registered_count": 1}
                        }
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return {"success": True}
            return {"error": "Event not found or student already registered"}
            
        except Exception as e:
            print(f"Error registering student: {str(e)}")
            return {"error": str(e)}
    
    def unregister_student(self, event_id: str, student_id: str) -> Dict[str, Any]:
        """
        Unregister a student from an event
        
        Args:
            event_id: Event ID
            student_id: Student ID
            
        Returns:
            dict: Success status or error
        """
        try:
            result = self.collection.update_one(
                {"event_id": event_id},
                {
                    "$pull": {"registered_students": student_id},
                    "$inc": {"registered_count": -1}
                }
            )
            
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(event_id)},
                        {
                            "$pull": {"registered_students": student_id},
                            "$inc": {"registered_count": -1}
                        }
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return {"success": True}
            return {"error": "Event not found or student not registered"}
            
        except Exception as e:
            print(f"Error unregistering student: {str(e)}")
            return {"error": str(e)}
