"""
Email service for sending emails via N8N webhook
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import requests
import random
from db import get_collection
from models.emails import EmailLog
from config import N8N_WEBHOOK_URL


class EmailService:
    """Service class for email CRUD operations"""
    
    def __init__(self):
        self.collection = get_collection("emails")
        self.webhook_url = N8N_WEBHOOK_URL
    
    def create_email_log(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new email log record
        
        Args:
            data: Email log data dictionary
            
        Returns:
            dict: Created email log with _id
        """
        try:
            # Validate with Pydantic model
            email = EmailLog(**data)
            
            # Convert to MongoDB document
            email_dict = email.to_mongo()
            if "_id" in email_dict:
                del email_dict["_id"]  # Let MongoDB generate ID
            
            # Insert into database
            result = self.collection.insert_one(email_dict)
            
            # Return created document
            created = self.collection.find_one({"_id": result.inserted_id})
            return self._serialize_document(created)
            
        except Exception as e:
            print(f"Error creating email log: {str(e)}")
            return {"error": str(e)}
    
    def list_email_logs(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List email logs with optional filters
        
        Args:
            filters: Optional MongoDB query filters
            
        Returns:
            List of email log dictionaries
        """
        try:
            query = filters if filters else {}
            emails_data = self.collection.find(query).sort("planned_send_time", -1)
            return [self._serialize_document(data) for data in emails_data]
            
        except Exception as e:
            print(f"Error listing email logs: {str(e)}")
            return []
    
    def get_email_log_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an email log by ID
        
        Args:
            email_id: Email log ID (MongoDB _id)
            
        Returns:
            Email log dictionary or None
        """
        try:
            email_data = self.collection.find_one({"_id": ObjectId(email_id)})
            
            if email_data:
                return self._serialize_document(email_data)
            return None
            
        except Exception as e:
            print(f"Error getting email log: {str(e)}")
            return None
    
    def update_email_log(self, email_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an email log
        
        Args:
            email_id: Email log ID
            updates: Dictionary of fields to update
            
        Returns:
            dict: Updated email log or error
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.now(timezone.utc)
            
            result = self.collection.update_one(
                {"_id": ObjectId(email_id)},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return self.get_email_log_by_id(email_id) or {"success": True}
            
            return {"error": "Email log not found or not modified"}
            
        except Exception as e:
            print(f"Error updating email log: {str(e)}")
            return {"error": str(e)}
    
    def delete_email_log(self, email_id: str) -> Dict[str, Any]:
        """
        Delete an email log (hard delete)
        
        Args:
            email_id: Email log ID
            
        Returns:
            dict: Success status
        """
        try:
            result = self.collection.delete_one({"_id": ObjectId(email_id)})
            
            if result.deleted_count > 0:
                return {"success": True, "deleted_count": result.deleted_count}
            
            return {"error": "Email log not found"}
            
        except Exception as e:
            print(f"Error deleting email log: {str(e)}")
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
    
    def create_email_record(self, email: EmailLog) -> str:
        """
        Legacy method - Create a new email record (use create_email_log instead)
        
        Args:
            email: EmailLog model instance
            
        Returns:
            str: ID of the created email record
        """
        email_dict = email.model_dump(exclude={"id"})
        result = self.collection.insert_one(email_dict)
        return str(result.inserted_id)
    
    def get_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Alias for get_email_log_by_id"""
        return self.get_email_log_by_id(email_id)
    
    def get_all_emails(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all email records (alias for list_email_logs)
        
        Args:
            status_filter: Filter by status (pending, sent, failed)
            
        Returns:
            List of email log dictionaries
        """
        filters = {"status": status_filter} if status_filter else None
        return self.list_email_logs(filters)
    
    def update_email(self, email_id: str, update_data: dict) -> Dict[str, Any]:
        """
        Legacy method - Update an email record (use update_email_log instead)
        
        Args:
            email_id: Email ID
            update_data: Dictionary of fields to update
            
        Returns:
            dict: Success status or error
        """
        return self.update_email_log(email_id, update_data)
    
    def send_email(
        self,
        recipient_email: str,
        recipient_role: str,
        subject: str,
        body: str,
        related_match_id: str = None
    ) -> tuple[bool, str]:
        """
        Send an email via N8N webhook
        
        Args:
            recipient_email: Email address of recipient
            recipient_role: Role of recipient (student, mentor, admin)
            subject: Email subject
            body: Email body
            related_match_id: Optional match ID if related to a match
            
        Returns:
            tuple: (success: bool, email_id: str)
        """
        # Create email record
        email = EmailLog(
            recipient_email=recipient_email,
            recipient_role=recipient_role,
            subject=subject,
            body=body,
            related_match_id=related_match_id,
            status="pending"
        )
        
        email_id = self.create_email_record(email)
        
        # Send via N8N webhook
        if not self.webhook_url:
            self.update_email(email_id, {
                "status": "failed",
                "failed_reason": "N8N webhook URL not configured"
            })
            return False, email_id
        
        try:
            payload = {
                "subject": subject,
                "body": body,
                "recipient": recipient_email
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                self.update_email(email_id, {
                    "status": "sent"
                })
                return True, email_id
            else:
                self.update_email(email_id, {
                    "status": "failed",
                    "error_message": f"HTTP {response.status_code}: {response.text}"
                })
                return False, email_id
                
        except Exception as e:
            self.update_email(email_id, {
                "status": "failed",
                "error_message": str(e)
            })
            return False, email_id
    
    def get_sent_emails(self, limit: int = 50) -> List[EmailLog]:
        """
        Get recently sent emails
        
        Args:
            limit: Maximum number of emails to return
            
        Returns:
            List of EmailLog objects
        """
        emails_data = self.collection.find({"status": "sent"}).sort("planned_send_time", -1).limit(limit)
        return [EmailLog.from_mongo(data) for data in emails_data]
    
    def get_failed_emails(self) -> List[EmailLog]:
        """
        Get failed emails
        
        Returns:
            List of EmailLog objects
        """
        return self.get_all_emails(status_filter="failed")
    
    def schedule_email(
        self,
        recipient_email: str,
        recipient_role: str,
        subject: str,
        body: str,
        related_match_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule an email for future delivery with human-like timing.
        
        Args:
            recipient_email: Email address of recipient
            recipient_role: Role of recipient (e.g., "mentor", "student")
            subject: Email subject line
            body: Email body content
            related_match_id: Optional ID of related match record
            
        Returns:
            dict: Created email log with scheduled time
        """
        # Compute human-like send time (between 15 minutes and 24 hours)
        min_delay_minutes = 15
        max_delay_minutes = 24 * 60  # 24 hours
        
        # Random delay in minutes
        delay_minutes = random.randint(min_delay_minutes, max_delay_minutes)
        
        # Calculate scheduled time
        now = datetime.now(timezone.utc)
        scheduled_time = now + timedelta(minutes=delay_minutes)
        
        # Add random seconds to avoid exact times (e.g., 9:17:23 instead of 9:00:00)
        random_seconds = random.randint(0, 59)
        scheduled_time = scheduled_time.replace(second=random_seconds, microsecond=0)
        
        # Create email log entry
        email_data = {
            "recipient_email": recipient_email,
            "recipient_role": recipient_role,
            "subject": subject,
            "body": body,
            "status": "scheduled",
            "planned_send_time": scheduled_time,
            "related_match_id": related_match_id,
            "created_at": now,
            "updated_at": now
        }
        
        return self.create_email_log(email_data)
    
    def send_due_emails(self) -> Dict[str, Any]:
        """
        Query all scheduled emails that are due for sending and send them via N8N webhook.
        
        Returns:
            dict: Summary of sending results
        """
        now = datetime.now(timezone.utc)
        
        # Find all emails that are scheduled and due to be sent
        due_emails = self.collection.find({
            "status": "scheduled",
            "planned_send_time": {"$lte": now}
        })
        
        results = {
            "total_processed": 0,
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for email_doc in due_emails:
            results["total_processed"] += 1
            email_id = str(email_doc["_id"])
            
            try:
                # Prepare payload for N8N webhook
                payload = {
                    "email": email_doc["recipient_email"],
                    "subject": email_doc["subject"],
                    "body": email_doc["body"]
                }
                
                # Send POST request to N8N webhook
                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    # Mark as sent
                    self.update_email_log(email_id, {
                        "status": "sent",
                        "sent_at": now
                    })
                    results["sent"] += 1
                    results["details"].append({
                        "email_id": email_id,
                        "recipient": email_doc["recipient_email"],
                        "status": "sent"
                    })
                else:
                    # Mark as failed
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    self.update_email_log(email_id, {
                        "status": "failed",
                        "error_message": error_msg
                    })
                    results["failed"] += 1
                    results["details"].append({
                        "email_id": email_id,
                        "recipient": email_doc["recipient_email"],
                        "status": "failed",
                        "error": error_msg
                    })
                    
            except Exception as e:
                # Mark as failed
                error_msg = str(e)
                self.update_email_log(email_id, {
                    "status": "failed",
                    "error_message": error_msg
                })
                results["failed"] += 1
                results["details"].append({
                    "email_id": email_id,
                    "recipient": email_doc.get("recipient_email", "unknown"),
                    "status": "failed",
                    "error": error_msg
                })
        
        return results
