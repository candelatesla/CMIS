"""
Mentoring Service for managing mentor-student relationships
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bson import ObjectId
from db import get_collection


class MentoringService:
    """Service for managing mentorship links and approvals"""
    
    def __init__(self):
        self.collection = get_collection("mentor_student_links")
    
    def _serialize_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB document to JSON-serializable format"""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    def assign_pending_match(self, student_id: str, mentor_id: str, match_reason: str) -> Dict[str, Any]:
        """
        Create a pending mentorship match from the matching engine
        
        Args:
            student_id: Student's ID (will be stored as string)
            mentor_id: Mentor's ID (will be stored as string)
            match_reason: Reason for the match
            
        Returns:
            Created link document or error
        """
        try:
            # Normalize IDs to strings (critical for query consistency)
            mentor_id = str(mentor_id)
            student_id = str(student_id)
            
            # Check if pending link already exists for this pair
            existing = self.collection.find_one({
                "student_id": student_id,
                "mentor_id": mentor_id,
                "status": "pending"
            })
            
            if existing:
                # Skip duplicate - return existing
                return self._serialize_document(existing)
            
            # Create new pending link with normalized lowercase status
            link_data = {
                "mentor_id": mentor_id,  # String, not ObjectId
                "student_id": student_id,  # String, not ObjectId
                "status": "pending",  # Lowercase
                "match_reason": match_reason,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = self.collection.insert_one(link_data)
            link_data["_id"] = str(result.inserted_id)
            
            return link_data
            
        except Exception as e:
            print(f"Error creating pending match: {str(e)}")
            return {"error": str(e)}
    
    def get_pending_requests_for_mentor(self, mentor_id: str) -> List[Dict[str, Any]]:
        """
        Get all pending mentorship requests for a mentor
        
        Args:
            mentor_id: Mentor's ID
            
        Returns:
            List of pending request documents with student info
        """
        try:
            from services.student_service import StudentService
            student_service = StudentService()
            
            # Normalize ID to string for query consistency
            mentor_id = str(mentor_id)
            
            # Find all pending links for this mentor (lowercase status)
            pending_links = list(self.collection.find({
                "mentor_id": mentor_id,
                "status": "pending"
            }))
            
            # Enrich with student data
            enriched_requests = []
            for link in pending_links:
                student_id = link.get("student_id")
                student = student_service.get_student_by_id(student_id)
                
                if student:
                    enriched_requests.append({
                        "link_id": str(link["_id"]),
                        "student": student,
                        "match_reason": link.get("match_reason", ""),
                        "created_at": link.get("created_at"),
                        "updated_at": link.get("updated_at")
                    })
            
            return enriched_requests
            
        except Exception as e:
            print(f"Error getting pending requests: {str(e)}")
            return []
    
    def accept_request(self, mentor_id: str, student_id: str) -> Dict[str, Any]:
        """
        Accept a mentorship request
        
        Args:
            mentor_id: Mentor's ID
            student_id: Student's ID
            
        Returns:
            Updated link document or error
        """
        try:
            # Normalize IDs to strings for query consistency
            mentor_id = str(mentor_id)
            student_id = str(student_id)
            
            result = self.collection.update_one(
                {
                    "mentor_id": mentor_id,
                    "student_id": student_id,
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "accepted",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                link = self.collection.find_one({
                    "mentor_id": mentor_id,
                    "student_id": student_id
                })
                return {"success": True, "link": self._serialize_document(link)}
            else:
                return {"error": "No pending request found"}
                
        except Exception as e:
            print(f"Error accepting request: {str(e)}")
            return {"error": str(e)}
    
    def decline_request(self, mentor_id: str, student_id: str) -> Dict[str, Any]:
        """
        Decline a mentorship request
        
        Args:
            mentor_id: Mentor's ID
            student_id: Student's ID
            
        Returns:
            Updated link document or error
        """
        try:
            # Normalize IDs to strings for query consistency
            mentor_id = str(mentor_id)
            student_id = str(student_id)
            
            result = self.collection.update_one(
                {
                    "mentor_id": mentor_id,
                    "student_id": student_id,
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "declined",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                return {"success": True}
            else:
                return {"error": "No pending request found"}
                
        except Exception as e:
            print(f"Error declining request: {str(e)}")
            return {"error": str(e)}
    
    def accept_request_by_link_id(self, link_id: str) -> Dict[str, Any]:
        """
        Accept a mentorship request using link ID (more reliable than mentor_id + student_id)
        
        Args:
            link_id: The mentorship link ID
            
        Returns:
            Updated link document or error
        """
        try:
            from bson import ObjectId
            
            result = self.collection.update_one(
                {
                    "_id": ObjectId(link_id),
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "accepted",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                link = self.collection.find_one({"_id": ObjectId(link_id)})
                return {"success": True, "link": self._serialize_document(link)}
            else:
                return {"error": "No pending request found"}
                
        except Exception as e:
            print(f"Error accepting request by link ID: {str(e)}")
            return {"error": str(e)}
    
    def decline_request_by_link_id(self, link_id: str) -> Dict[str, Any]:
        """
        Decline a mentorship request using link ID (more reliable than mentor_id + student_id)
        
        Args:
            link_id: The mentorship link ID
            
        Returns:
            Success status or error
        """
        try:
            from bson import ObjectId
            
            result = self.collection.update_one(
                {
                    "_id": ObjectId(link_id),
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "declined",
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )
            
            if result.modified_count > 0:
                return {"success": True}
            else:
                return {"error": "No pending request found"}
                
        except Exception as e:
            print(f"Error declining request by link ID: {str(e)}")
            return {"error": str(e)}
    
    def get_student_mentor(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        Get accepted mentor for a student
        
        Args:
            student_id: Student's ID
            
        Returns:
            Mentor data with link info or None
        """
        try:
            from services.mentor_service import MentorService
            mentor_service = MentorService()
            
            # Normalize ID to string for query consistency
            student_id = str(student_id)
            
            # Find accepted or pending link (lowercase status)
            link = self.collection.find_one({
                "student_id": student_id,
                "status": {"$in": ["accepted", "pending"]}
            })
            
            if not link:
                return None
            
            # Get mentor details
            mentor_id = link.get("mentor_id")
            mentor = mentor_service.get_mentor_by_id(mentor_id)
            
            if mentor:
                mentor["mentorship_status"] = link.get("status")
                mentor["match_reason"] = link.get("match_reason", "")
                mentor["matched_at"] = link.get("created_at")
            
            return mentor
            
        except Exception as e:
            print(f"Error getting student mentor: {str(e)}")
            return None
    
    def get_students_mentored_by(self, mentor_id: str) -> List[Dict[str, Any]]:
        """
        Get all accepted students for a mentor
        
        Args:
            mentor_id: Mentor's ID
            
        Returns:
            List of student documents with link info
        """
        try:
            from services.student_service import StudentService
            student_service = StudentService()
            
            # Normalize ID to string for query consistency
            mentor_id = str(mentor_id)
            
            # Find all accepted links for this mentor (lowercase status)
            accepted_links = list(self.collection.find({
                "mentor_id": mentor_id,
                "status": "accepted"
            }))
            
            # Enrich with student data
            enriched_students = []
            for link in accepted_links:
                student_id = link.get("student_id")
                student = student_service.get_student_by_id(student_id)
                
                if student:
                    student["match_reason"] = link.get("match_reason", "")
                    student["matched_at"] = link.get("created_at")
                    enriched_students.append(student)
            
            return enriched_students
            
        except Exception as e:
            print(f"Error getting mentored students: {str(e)}")
            return []
    
    def get_all_links(self) -> List[Dict[str, Any]]:
        """
        Get all mentorship links for admin tracking
        
        Returns:
            List of all links with student and mentor info
        """
        try:
            from services.student_service import StudentService
            from services.mentor_service import MentorService
            
            student_service = StudentService()
            mentor_service = MentorService()
            
            all_links = list(self.collection.find({}))
            
            # Enrich with student and mentor data
            enriched_links = []
            for link in all_links:
                student_id = link.get("student_id")
                mentor_id = link.get("mentor_id")
                
                student = student_service.get_student_by_id(student_id)
                mentor = mentor_service.get_mentor_by_id(mentor_id)
                
                if student and mentor:
                    enriched_links.append({
                        "link_id": str(link["_id"]),
                        "student_name": student.get("name", "Unknown"),
                        "student_email": student.get("email", "N/A"),
                        "mentor_name": mentor.get("name", "Unknown"),
                        "mentor_email": mentor.get("email", "N/A"),
                        "status": link.get("status", "unknown"),
                        "match_reason": link.get("match_reason", ""),
                        "created_at": link.get("created_at"),
                        "updated_at": link.get("updated_at")
                    })
            
            return enriched_links
            
        except Exception as e:
            print(f"Error getting all links: {str(e)}")
            return []
