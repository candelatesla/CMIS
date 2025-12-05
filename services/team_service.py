"""
Team service for team registration and management
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from db import get_collection


class TeamService:
    """Service class for team CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("teams")
    
    def create_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new team
        
        Args:
            team_data: Team data dictionary
            
        Returns:
            dict: Created team with _id
        """
        try:
            # Add timestamps
            team_data["created_at"] = datetime.utcnow()
            team_data["updated_at"] = datetime.utcnow()
            
            # Insert into database
            result = self.collection.insert_one(team_data)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating team: {str(e)}")
            return {"error": str(e)}
    
    def get_teams_for_student(self, student_id: str, student_email: str = None) -> List[Dict[str, Any]]:
        """
        Get all teams for a student (either as creator or member)
        
        Args:
            student_id: Student ID
            student_email: Optional student email to match members
            
        Returns:
            List of team dictionaries
        """
        try:
            # Build query - find teams where:
            # 1. Student created the team
            # 2. Student is a member (by linked_student_id)
            # 3. Student email matches a member email
            query = {
                "$or": [
                    {"created_by_student_id": student_id}
                ]
            }
            
            # Add member matching conditions
            if student_email:
                query["$or"].extend([
                    {"members.linked_student_id": student_id},
                    {"members.email": student_email}
                ])
            else:
                query["$or"].append({"members.linked_student_id": student_id})
            
            teams = self.collection.find(query).sort("created_at", -1)
            return [self._serialize_document(team) for team in teams]
            
        except Exception as e:
            print(f"Error getting teams for student: {str(e)}")
            return []
    
    def get_team_by_id(self, team_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a team by ID
        
        Args:
            team_id: Team MongoDB _id
            
        Returns:
            Team dictionary or None
        """
        try:
            team = self.collection.find_one({"_id": ObjectId(team_id)})
            return self._serialize_document(team) if team else None
            
        except Exception as e:
            print(f"Error getting team by ID: {str(e)}")
            return None
    
    def update_team(self, team_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a team
        
        Args:
            team_id: Team MongoDB _id
            updates: Dictionary of fields to update
            
        Returns:
            Updated team or error dict
        """
        try:
            updates["updated_at"] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(team_id)},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"error": "Team not found"}
            
            updated = self.collection.find_one({"_id": ObjectId(team_id)})
            return self._serialize_document(updated)
            
        except Exception as e:
            print(f"Error updating team: {str(e)}")
            return {"error": str(e)}
    
    def link_members_to_students(self, members: List[Dict[str, Any]], student_service) -> List[Dict[str, Any]]:
        """
        Link team members to existing students by email
        
        Args:
            members: List of member dictionaries with email
            student_service: StudentService instance
            
        Returns:
            List of members with linked_student_id populated where match found
        """
        try:
            linked_members = []
            
            for member in members:
                member_copy = member.copy()
                email = member.get("email", "").strip().lower()
                
                if email:
                    # Try to find student by email
                    students = student_service.list_students()
                    matching_student = None
                    
                    for student in students:
                        if student.get("email", "").strip().lower() == email:
                            matching_student = student
                            break
                    
                    if matching_student:
                        member_copy["linked_student_id"] = matching_student.get("student_id")
                    else:
                        member_copy["linked_student_id"] = None
                else:
                    member_copy["linked_student_id"] = None
                
                linked_members.append(member_copy)
            
            return linked_members
            
        except Exception as e:
            print(f"Error linking members to students: {str(e)}")
            return members
    
    def get_teams_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """
        Get all teams for a specific event
        
        Args:
            event_id: Event ID
            
        Returns:
            List of team dictionaries
        """
        try:
            teams = self.collection.find({"event_id": event_id}).sort("created_at", -1)
            return [self._serialize_document(team) for team in teams]
            
        except Exception as e:
            print(f"Error getting teams by event: {str(e)}")
            return []
    
    def get_teams_assigned_to_judge(self, judge_id: str) -> List[Dict[str, Any]]:
        """
        Get all teams assigned to a specific judge
        
        Args:
            judge_id: Judge/Mentor ID (string)
            
        Returns:
            List of team dictionaries
        """
        try:
            # Normalize ID to string for consistent querying
            judge_id = str(judge_id)
            
            # Find teams where judge is in judges_assigned array
            teams = self.collection.find({
                "judges_assigned": judge_id
            }).sort("created_at", -1)
            return [self._serialize_document(team) for team in teams]
            
        except Exception as e:
            print(f"Error getting teams for judge: {str(e)}")
            return []
    
    def save_judge_score(self, team_id: str, judge_id: str, score: float, comments: str = "") -> Dict[str, Any]:
        """
        Save a judge's score for a team
        
        Args:
            team_id: Team ID
            judge_id: Judge/Mentor ID (string)
            score: Numeric score (0-100)
            comments: Optional comments from judge
            
        Returns:
            Updated team or error dict
        """
        try:
            # Normalize IDs to strings
            judge_id = str(judge_id)
            
            # Get current team
            team = self.get_team_by_id(team_id)
            if not team:
                return {"error": "Team not found"}
            
            # Initialize judge_scores if not exists
            judge_scores = team.get("judge_scores", {})
            
            # Add/update this judge's score
            judge_scores[judge_id] = {
                "score": score,
                "comments": comments,
                "submitted_at": datetime.utcnow().isoformat()
            }
            
            # Check if all judges have submitted (using string IDs)
            judges_assigned = [str(j) for j in team.get("judges_assigned", [])]
            all_submitted = len(judge_scores) == len(judges_assigned) if judges_assigned else False
            
            # Calculate final score if all judges submitted
            final_score = None
            if all_submitted and len(judge_scores) > 0:
                scores_list = [js.get("score", 0) for js in judge_scores.values()]
                final_score = sum(scores_list) / len(scores_list)
            
            # Update team
            updates = {
                "judge_scores": judge_scores,
                "updated_at": datetime.utcnow()
            }
            
            if final_score is not None:
                updates["final_score"] = final_score
                updates["status"] = "scored"
            
            result = self.collection.update_one(
                {"_id": ObjectId(team_id)},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"error": "Team not found"}
            
            updated = self.collection.find_one({"_id": ObjectId(team_id)})
            return self._serialize_document(updated)
            
        except Exception as e:
            print(f"Error saving judge score: {str(e)}")
            return {"error": str(e)}
    
    def assign_judges_to_team(self, team_id: str, judge_ids: List[str]) -> Dict[str, Any]:
        """
        Assign judges to a team
        
        Args:
            team_id: Team ID
            judge_ids: List of judge/mentor IDs
            
        Returns:
            Updated team or error dict
        """
        try:
            updates = {
                "judges_assigned": judge_ids,
                "updated_at": datetime.utcnow()
            }
            
            result = self.collection.update_one(
                {"_id": ObjectId(team_id)},
                {"$set": updates}
            )
            
            if result.matched_count == 0:
                return {"error": "Team not found"}
            
            updated = self.collection.find_one({"_id": ObjectId(team_id)})
            return self._serialize_document(updated)
            
        except Exception as e:
            print(f"Error assigning judges: {str(e)}")
            return {"error": str(e)}
    
    def _serialize_document(self, doc: Optional[Dict]) -> Optional[Dict]:
        """Convert MongoDB document to JSON-serializable dict"""
        if not doc:
            return None
        
        doc_copy = doc.copy()
        if "_id" in doc_copy:
            doc_copy["_id"] = str(doc_copy["_id"])
        if "event_id" in doc_copy and isinstance(doc_copy["event_id"], ObjectId):
            doc_copy["event_id"] = str(doc_copy["event_id"])
        
        # Handle datetime objects
        for key, value in doc_copy.items():
            if isinstance(value, datetime):
                doc_copy[key] = value.isoformat()
        
        return doc_copy
