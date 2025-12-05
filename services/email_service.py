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
from config import N8N_WEBHOOK_URL, get_safe_test_mode, get_safe_test_emails
from utils.time_utils import get_human_like_schedule_time


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
        
        Uses refined scheduling logic:
        - Before 8 AM: Schedule between 8-10 AM today
        - 8 AM - 5 PM: Schedule after 10-25 minutes
        - After 5 PM: Schedule next day between 8-10 AM
        
        Args:
            recipient_email: Email address of recipient
            recipient_role: Role of recipient (e.g., "mentor", "student")
            subject: Email subject line
            body: Email body content
            related_match_id: Optional ID of related match record
            
        Returns:
            dict: Created email log with scheduled time
        """
        # Get human-like scheduled time using refined logic
        scheduled_time = get_human_like_schedule_time()
        
        # Get current time for created_at
        now = datetime.now(timezone.utc)
        
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
        
        In Safe Test Mode (SAFE_TEST_MODE=true), emails are redirected to test addresses
        instead of real recipients to avoid polluting production inboxes.
        
        Returns:
            dict: Summary of sending results
        """
        now = datetime.now(timezone.utc)
        
        # Check Safe Test Mode
        safe_mode = get_safe_test_mode()
        test_emails = get_safe_test_emails() if safe_mode else []
        test_email_index = 0  # Rotating index for test emails
        
        # Find all emails that are scheduled and due to be sent
        due_emails = self.collection.find({
            "status": "scheduled",
            "planned_send_time": {"$lte": now}
        })
        
        results = {
            "total_processed": 0,
            "sent": 0,
            "failed": 0,
            "safe_test_mode": safe_mode,
            "details": []
        }
        
        for email_doc in due_emails:
            results["total_processed"] += 1
            email_id = str(email_doc["_id"])
            original_recipient = email_doc["recipient_email"]
            
            try:
                # Determine actual recipient email
                if safe_mode and test_emails:
                    # Rotate through test emails
                    actual_recipient = test_emails[test_email_index % len(test_emails)]
                    test_email_index += 1
                else:
                    actual_recipient = original_recipient
                
                # Prepare payload for N8N webhook
                payload = {
                    "email": actual_recipient,
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
                    update_data = {
                        "status": "sent",
                        "actual_send_time": now,
                        "sent_at": now
                    }
                    # Store actual sent email if redirected in safe mode
                    if safe_mode and actual_recipient != original_recipient:
                        update_data["actual_recipient"] = actual_recipient
                    
                    self.update_email_log(email_id, update_data)
                    results["sent"] += 1
                    
                    detail = {
                        "email_id": email_id,
                        "original_recipient": original_recipient,
                        "status": "sent"
                    }
                    if safe_mode and actual_recipient != original_recipient:
                        detail["redirected_to"] = actual_recipient
                    results["details"].append(detail)
                else:
                    # Mark as failed
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    self.update_email_log(email_id, {
                        "status": "failed",
                        "actual_send_time": now,
                        "error_message": error_msg
                    })
                    results["failed"] += 1
                    results["details"].append({
                        "email_id": email_id,
                        "original_recipient": original_recipient,
                        "status": "failed",
                        "error": error_msg
                    })
                    
            except Exception as e:
                # Mark as failed
                error_msg = str(e)
                self.update_email_log(email_id, {
                    "status": "failed",
                    "actual_send_time": now,
                    "error_message": error_msg
                })
                results["failed"] += 1
                results["details"].append({
                    "email_id": email_id,
                    "original_recipient": email_doc.get("recipient_email", "unknown"),
                    "status": "failed",
                    "error": error_msg
                })
        
        return results
    
    def list_scheduled_emails(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled emails (future emails in queue)
        
        Returns:
            List of scheduled email dictionaries sorted by planned_send_time (ascending)
        """
        try:
            now = datetime.now(timezone.utc)
            emails_data = self.collection.find({
                "status": "scheduled",
                "planned_send_time": {"$gt": now}
            }).sort("planned_send_time", 1)  # 1 = ascending
            
            return [self._serialize_document(data) for data in emails_data]
        except Exception as e:
            print(f"Error listing scheduled emails: {str(e)}")
            return []
    
    def list_sent_emails(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all sent emails
        
        Args:
            limit: Maximum number of emails to return (default 100)
            
        Returns:
            List of sent email dictionaries sorted by actual_send_time (descending)
        """
        try:
            # Sort by actual_send_time if available, otherwise sent_at, otherwise planned_send_time
            emails_data = list(self.collection.find({
                "status": "sent"
            }).limit(limit))
            
            # Sort in Python to handle missing fields
            emails_data.sort(
                key=lambda x: x.get("actual_send_time") or x.get("sent_at") or x.get("planned_send_time") or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True
            )
            
            return [self._serialize_document(data) for data in emails_data]
        except Exception as e:
            print(f"Error listing sent emails: {str(e)}")
            return []
    
    def list_failed_emails(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all failed emails
        
        Args:
            limit: Maximum number of emails to return (default 100)
            
        Returns:
            List of failed email dictionaries sorted by actual_send_time (descending)
        """
        try:
            # Sort by actual_send_time if available, otherwise planned_send_time
            emails_data = list(self.collection.find({
                "status": "failed"
            }).limit(limit))
            
            # Sort in Python to handle missing fields
            emails_data.sort(
                key=lambda x: x.get("actual_send_time") or x.get("planned_send_time") or datetime.min.replace(tzinfo=timezone.utc),
                reverse=True
            )
            
            return [self._serialize_document(data) for data in emails_data]
        except Exception as e:
            print(f"Error listing failed emails: {str(e)}")
            return []
