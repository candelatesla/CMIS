"""
Email service for sending emails via N8N webhook
"""
from typing import List, Optional, Dict, Any, Tuple
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
    
    def send_team_registration_email(self, member_email: str, member_name: str, 
                                     event_name: str, event_date: str, team_name: str, 
                                     all_members: List[str]) -> bool:
        """
        Send team registration confirmation email
        
        Args:
            member_email: Email address of team member
            member_name: Name of team member
            event_name: Name of the event
            event_date: Date of the event
            team_name: Name of the team
            all_members: List of all team member names
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Import formatting utilities
        from utils.email_formatting import build_team_registration_email_html
        
        # Use HTML formatter
        subject, body = build_team_registration_email_html(
            member_name=member_name,
            event_name=event_name,
            event_date=event_date,
            team_name=team_name,
            all_members=all_members
        )
        
        try:
            if not self.webhook_url:
                print(f"N8N webhook URL not configured - email not sent to {member_email}")
                return False
            
            # n8n webhook expects "email" not "recipient"
            payload = {
                "email": member_email,
                "subject": subject,
                "body": body
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Team registration email sent to {member_email}")
                return True
            else:
                print(f"❌ Failed to send email to {member_email}: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email to {member_email}: {str(e)}")
            return False
    
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
    
    def send_mentor_match_email(self, mentor_email: str, mentor_name: str, subject: str, body: str, match_id: str = None) -> Tuple[bool, str]:
        """
        Send a mentor match email immediately (wrapper around send_email)
        
        Args:
            mentor_email: Mentor's email address
            mentor_name: Mentor's name
            subject: Email subject line
            body: Email body (HTML)
            match_id: Optional match ID to associate with email
            
        Returns:
            Tuple of (success: bool, email_id: str)
        """
        return self.send_email(
            recipient_email=mentor_email,
            recipient_role="mentor",
            subject=subject,
            body=body,
            related_match_id=match_id
        )
    
    def mark_email_sent(self, email_id: str) -> bool:
        """
        Mark a scheduled email as sent immediately
        
        Args:
            email_id: ID of the email to mark as sent
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.update_email_log(email_id, {
                "status": "sent",
                "actual_send_time": datetime.now(timezone.utc)
            })
            return result is not None
        except Exception as e:
            print(f"Error marking email as sent: {str(e)}")
            return False
    
    def build_team_score_email_plain(self, student_name: str, event_name: str, team_name: str, 
                                     mentor_name: str, score: float, comments: str) -> str:
        """
        Build plain text score notification email
        
        Args:
            student_name: Name of the student
            event_name: Name of the event
            team_name: Name of the team
            mentor_name: Name of the judge/mentor
            score: Score given by judge
            comments: Comments from judge
            
        Returns:
            Plain text email body
        """
        return f"""Dear {student_name},

Your team has been scored for the {event_name}.

Team: {team_name}
Judge: {mentor_name}
Score: {score}

Comments:
{comments or "No comments provided."}

You can now view your score in your Student Dashboard under 'My Scores'.

Best regards,
CMIS Engagement Platform
Texas A&M University""".strip()
    
    def build_team_score_email_html(self, student_name: str, event_name: str, team_name: str,
                                    mentor_name: str, score: float, comments: str) -> str:
        """
        Build HTML score notification email
        
        Args:
            student_name: Name of the student
            event_name: Name of the event
            team_name: Name of the team
            mentor_name: Name of the judge/mentor
            score: Score given by judge
            comments: Comments from judge
            
        Returns:
            HTML formatted email body
        """
        return f"""<p>Dear {student_name},</p>

<p>Your team has been scored for the <strong>{event_name}</strong>.</p>

<h3>Score Details</h3>
<ul>
  <li><strong>Team:</strong> {team_name}</li>
  <li><strong>Judge:</strong> {mentor_name}</li>
  <li><strong>Score:</strong> {score}</li>
</ul>

<h3>Judge Comments</h3>
<p>{comments or "No comments were provided."}</p>

<p>You can now view your score anytime in your Student Dashboard under <strong>My Scores</strong>.</p>

<p>Best regards,<br>
<strong>CMIS Engagement Platform</strong><br>
Texas A&amp;M University</p>"""
    
    def send_team_score_notification(self, team: Dict[str, Any], mentor: Dict[str, Any], 
                                     score: float, comments: str) -> int:
        """
        Send score notification emails to all team members
        
        Args:
            team: Team document with event_id, team_name, members[]
            mentor: Mentor/judge document with name
            score: Score given
            comments: Comments from judge
            
        Returns:
            Number of emails successfully sent
        """
        try:
            # Import EventService here to avoid circular import
            from services.event_service import EventService
            event_service = EventService()
            
            # Get event details
            event = event_service.get_event_by_id(team.get("event_id"))
            if not event:
                print(f"Error: Event not found for team {team.get('team_name')}")
                return 0
            
            event_name = event.get("name", "Unknown Event")
            team_name = team.get("team_name", "Unknown Team")
            mentor_name = mentor.get("name", "Unknown Judge")
            
            sent_count = 0
            members = team.get("members", [])
            
            for member in members:
                name = member.get("name", "Student")
                email = member.get("email")
                
                if not email:
                    continue
                
                try:
                    # Try HTML format first
                    body = self.build_team_score_email_html(
                        student_name=name,
                        event_name=event_name,
                        team_name=team_name,
                        mentor_name=mentor_name,
                        score=score,
                        comments=comments
                    )
                except Exception as e:
                    print(f"Error building HTML email, using plain text: {str(e)}")
                    # Fallback to plain text
                    body = self.build_team_score_email_plain(
                        student_name=name,
                        event_name=event_name,
                        team_name=team_name,
                        mentor_name=mentor_name,
                        score=score,
                        comments=comments
                    )
                
                # Send via N8N webhook
                try:
                    payload = {
                        "email": email,
                        "subject": f"Your Team Score – {event_name}",
                        "body": body
                    }
                    
                    response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        sent_count += 1
                        print(f"Score notification sent to {email}")
                    else:
                        print(f"Failed to send score notification to {email}: {response.status_code}")
                        
                except Exception as e:
                    print(f"Error sending score notification to {email}: {str(e)}")
            
            return sent_count
            
        except Exception as e:
            print(f"Error in send_team_score_notification: {str(e)}")
            return 0
    
    # ========================================================================
    # MENTORSHIP ACCEPTANCE EMAILS
    # ========================================================================
    
    def build_mentor_accept_email_html(
        self,
        student: Dict[str, Any],
        mentor: Dict[str, Any],
        match_reason: str
    ) -> str:
        """
        Build HTML email for student when mentor accepts mentorship
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            match_reason: Why they were matched
            
        Returns:
            HTML email body
        """
        return f"""
<p>Dear {student.get('name', 'Student')},</p>

<p>Great news! Your assigned mentor, <strong>{mentor.get('name', 'N/A')}</strong>, has accepted your mentorship request through the CMIS Engagement Platform.</p>

<h3>Mentor Information</h3>
<ul>
  <li><strong>Name:</strong> {mentor.get('name', 'N/A')}</li>
  <li><strong>Email:</strong> {mentor.get('email', 'N/A')}</li>
  <li><strong>Company:</strong> {mentor.get('company', 'N/A')}</li>
  <li><strong>Role:</strong> {mentor.get('job_title', 'N/A')}</li>
</ul>

<h3>Why You Were Matched</h3>
<p>{match_reason}</p>

<p>You can now view your mentor's full profile under <strong>My Assigned Mentor</strong> in your Student Dashboard.</p>

<p>Please reach out to your mentor to schedule your first meeting.</p>

<p>Best regards,<br>
<strong>CMIS Engagement Platform</strong><br>
Texas A&M University</p>
"""
    
    def build_mentor_accept_email_plain(
        self,
        student: Dict[str, Any],
        mentor: Dict[str, Any],
        match_reason: str
    ) -> str:
        """
        Build plain text email for student when mentor accepts mentorship
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            match_reason: Why they were matched
            
        Returns:
            Plain text email body
        """
        return f"""
Dear {student.get('name', 'Student')},

Great news! Your assigned mentor, {mentor.get('name', 'N/A')}, has accepted your mentorship request.

Mentor Details:
- Name: {mentor.get('name', 'N/A')}
- Email: {mentor.get('email', 'N/A')}
- Company: {mentor.get('company', 'N/A')}
- Role: {mentor.get('job_title', 'N/A')}

Why you were matched:
{match_reason}

You can now see your assigned mentor inside your Student Dashboard.

Please reach out to schedule your first meeting.

Best regards,
CMIS Engagement Platform
Texas A&M University
""".strip()
    
    def build_mentor_accept_confirmation_email_html(
        self,
        student: Dict[str, Any],
        mentor: Dict[str, Any],
        match_reason: str
    ) -> str:
        """
        Build HTML confirmation email for mentor after accepting student
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            match_reason: Why they were matched
            
        Returns:
            HTML email body
        """
        return f"""
<p>Dear {mentor.get('name', 'Mentor')},</p>

<p>Thank you for confirming your mentorship assignment in the CMIS Engagement Platform.</p>

<p>You have now been officially assigned as a mentor to the following student:</p>

<h3>Student Information</h3>
<ul>
  <li><strong>Name:</strong> {student.get('name', 'N/A')}</li>
  <li><strong>Email:</strong> {student.get('email', 'N/A')}</li>
  <li><strong>Major:</strong> {student.get('major', 'N/A')}</li>
  <li><strong>Graduation Year:</strong> {student.get('graduation_year', student.get('year', 'N/A'))}</li>
</ul>

<h3>Why You Were Matched</h3>
<p>{match_reason}</p>

<p>Please reach out to the student to schedule your first meeting.</p>

<p>Thank you for supporting students at Texas A&M University.</p>

<p>Best regards,<br>
<strong>CMIS Engagement Platform</strong><br>
Texas A&M University</p>
"""
    
    def build_mentor_accept_confirmation_email_plain(
        self,
        student: Dict[str, Any],
        mentor: Dict[str, Any],
        match_reason: str
    ) -> str:
        """
        Build plain text confirmation email for mentor after accepting student
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            match_reason: Why they were matched
            
        Returns:
            Plain text email body
        """
        return f"""
Dear {mentor.get('name', 'Mentor')},

Thank you for accepting your mentorship assignment.

Student Details:
- Name: {student.get('name', 'N/A')}
- Email: {student.get('email', 'N/A')}
- Major: {student.get('major', 'N/A')}
- Graduation Year: {student.get('graduation_year', student.get('year', 'N/A'))}

Why you were matched:
{match_reason}

Please reach out to the student to schedule your first meeting.

Best regards,
CMIS Engagement Platform
Texas A&M University
""".strip()
    
    def send_mentor_acceptance_email(
        self,
        student: Dict[str, Any],
        mentor: Dict[str, Any],
        match_reason: str
    ) -> bool:
        """
        Send acceptance email to student when mentor accepts mentorship
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            match_reason: Why they were matched
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Try HTML format first
            try:
                body = self.build_mentor_accept_email_html(student, mentor, match_reason)
            except Exception as e:
                print(f"Error building HTML email, using plain text: {str(e)}")
                body = self.build_mentor_accept_email_plain(student, mentor, match_reason)
            
            payload = {
                "email": student.get("email"),
                "subject": f"Your Mentor Has Accepted – {mentor.get('name', 'Your Mentor')}",
                "body": body
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"Mentor acceptance email sent to student: {student.get('email')}")
                return True
            else:
                print(f"Failed to send mentor acceptance email: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending mentor acceptance email: {str(e)}")
            return False
    
    def send_mentor_accept_confirmation_email(
        self,
        student: Dict[str, Any],
        mentor: Dict[str, Any],
        match_reason: str
    ) -> bool:
        """
        Send confirmation email to mentor after accepting student
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            match_reason: Why they were matched
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Try HTML format first
            try:
                body = self.build_mentor_accept_confirmation_email_html(student, mentor, match_reason)
            except Exception as e:
                print(f"Error building HTML email, using plain text: {str(e)}")
                body = self.build_mentor_accept_confirmation_email_plain(student, mentor, match_reason)
            
            payload = {
                "email": mentor.get("email"),
                "subject": f"You've Been Assigned a Student – {student.get('name', 'Student')}",
                "body": body
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"Mentor confirmation email sent to mentor: {mentor.get('email')}")
                return True
            else:
                print(f"Failed to send mentor confirmation email: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending mentor confirmation email: {str(e)}")
            return False
    
    def build_judge_assignment_email_html(
        self,
        judge: Dict[str, Any],
        event: Dict[str, Any]
    ) -> str:
        """
        Build HTML email for judge assignment notification
        
        Args:
            judge: Judge dictionary
            event: Event dictionary
            
        Returns:
            str: HTML email body
        """
        from datetime import date
        
        judge_name = judge.get('name', 'Judge')
        event_name = event.get('name', 'Event')
        today = date.today().strftime("%B %d, %Y")
        
        return f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <p>Howdy {judge_name},</p>
    
    <p>You have been added as a judge for the <strong>{event_name}</strong> through the CMIS Engagement Platform.</p>
    
    <h3 style="color: #500000;">Event Details</h3>
    <ul style="line-height: 1.8;">
        <li><strong>Event:</strong> {event_name}</li>
        <li><strong>Date:</strong> Today, {today}</li>
        <li><strong>Judging Window:</strong> 9:00 AM – 5:00 PM</li>
    </ul>
    
    <p>You can now log into your Judge Dashboard to view the teams registered for this event and begin scoring once submissions are available.</p>
    
    <p>Thank you for supporting CMIS and mentoring students at Texas A&M University.</p>
    
    <p>Gig 'em,<br>
    <strong>CMIS Engagement Platform</strong></p>
</div>
"""
    
    def build_judge_assignment_email_plain(
        self,
        judge: Dict[str, Any],
        event: Dict[str, Any]
    ) -> str:
        """
        Build plain text email for judge assignment notification
        
        Args:
            judge: Judge dictionary
            event: Event dictionary
            
        Returns:
            str: Plain text email body
        """
        from datetime import date
        
        judge_name = judge.get('name', 'Judge')
        event_name = event.get('name', 'Event')
        today = date.today().strftime("%B %d, %Y")
        
        return f"""
Howdy {judge_name},

You have been added as a judge for the {event_name}.

Event Details:
- Event: {event_name}
- Date: Today, {today}
- Judging Window: 9:00 AM – 5:00 PM

You can now log into your Judge Dashboard to view registered teams and begin scoring.

Gig 'em,
CMIS Engagement Platform
"""
    
    def send_judge_assignment_email(
        self,
        judge: Dict[str, Any],
        event: Dict[str, Any]
    ) -> bool:
        """
        Send judge assignment notification email
        
        Args:
            judge: Judge dictionary
            event: Event dictionary
            
        Returns:
            bool: True if sent successfully
        """
        try:
            # Try HTML format first
            try:
                body = self.build_judge_assignment_email_html(judge, event)
            except Exception as e:
                print(f"Error building HTML email, using plain text: {str(e)}")
                body = self.build_judge_assignment_email_plain(judge, event)
            
            event_name = event.get('name', 'Event')
            
            payload = {
                "email": judge.get("email"),
                "subject": f"You've Been Added as a Judge – {event_name}",
                "body": body
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"Judge assignment email sent to: {judge.get('email')}")
                return True
            else:
                print(f"Failed to send judge assignment email: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error sending judge assignment email: {str(e)}")
            return False
