"""
Student service for database operations
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection
from models.students import Student


class StudentService:
    """Service class for student CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("students")
    
    def create_student(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new student
        
        Args:
            data: Student data dictionary
            
        Returns:
            dict: Created student with _id
        """
        try:
            # Validate with Pydantic model
            student = Student(**data)
            
            # Convert to MongoDB document
            student_dict = student.to_mongo()
            if "_id" in student_dict:
                del student_dict["_id"]  # Let MongoDB generate ID
            
            # Insert into database
            result = self.collection.insert_one(student_dict)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating student: {str(e)}")
            return {"error": str(e)}
    
    def list_students(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List students with optional filters
        
        Args:
            filters: Optional MongoDB query filters
            
        Returns:
            List of student dictionaries
        """
        try:
            query = filters if filters else {}
            students_data = self.collection.find(query)
            return [self._serialize_document(data) for data in students_data]
            
        except Exception as e:
            print(f"Error listing students: {str(e)}")
            return []
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a student by ID
        
        Args:
            student_id: Student ID (either student_id field or MongoDB _id)
            
        Returns:
            Student dictionary or None
        """
        try:
            # Try finding by student_id field first
            student_data = self.collection.find_one({"student_id": student_id})
            
            # If not found, try by MongoDB _id
            if not student_data:
                try:
                    student_data = self.collection.find_one({"_id": ObjectId(student_id)})
                except:
                    pass
            
            if student_data:
                return self._serialize_document(student_data)
            return None
            
        except Exception as e:
            print(f"Error getting student: {str(e)}")
            return None
    
    def get_student_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get a student by email
        
        Args:
            email: Student email address
            
        Returns:
            Student dictionary or None
        """
        try:
            student_data = self.collection.find_one({"email": email})
            
            if student_data:
                return self._serialize_document(student_data)
            return None
            
        except Exception as e:
            print(f"Error getting student by email: {str(e)}")
            return None
    
    def update_student(self, student_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a student
        
        Args:
            student_id: Student ID
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated student or error
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(timezone.utc)
            
            # Try updating by student_id field first
            result = self.collection.update_one(
                {"student_id": student_id},
                {"$set": updates}
            )
            
            # If not found, try by MongoDB _id
            if result.matched_count == 0:
                try:
                    result = self.collection.update_one(
                        {"_id": ObjectId(student_id)},
                        {"$set": updates}
                    )
                except:
                    pass
            
            if result.modified_count > 0:
                return self.get_student_by_id(student_id) or {"success": True}
            
            return {"error": "Student not found or not modified"}
            
        except Exception as e:
            print(f"Error updating student: {str(e)}")
            return {"error": str(e)}
    
    def delete_student(self, student_id: str) -> Dict[str, Any]:
        """
        Delete a student (hard delete)
        
        Args:
            student_id: Student ID
            
        Returns:
            dict: Success status
        """
        try:
            # Try deleting by student_id field first
            result = self.collection.delete_one({"student_id": student_id})
            
            # If not found, try by MongoDB _id
            if result.deleted_count == 0:
                try:
                    result = self.collection.delete_one({"_id": ObjectId(student_id)})
                except:
                    pass
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            
            return {"error": "Student not found"}
            
        except Exception as e:
            print(f"Error deleting student: {str(e)}")
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
