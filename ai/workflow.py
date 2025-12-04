"""
AI workflow engine for orchestrating complex tasks
Combines matching, email generation, and automation
"""
from typing import List, Dict, Any, Optional
from .matching import MatchingEngine
from .email_generation import EmailGenerator, generate_mentor_outreach_email
from services.student_service import StudentService
from services.mentor_service import MentorService
from services.match_service import MatchService
from services.email_service import EmailService


class WorkflowEngine:
    """Workflow engine for orchestrating AI-powered tasks"""
    
    def __init__(self):
        """Initialize the workflow engine"""
        self.matching_engine = MatchingEngine()
        self.email_generator = EmailGenerator()
        self.student_service = StudentService()
        self.mentor_service = MentorService()
        self.match_service = MatchService()
        self.email_service = EmailService()
    
    def run_auto_matching_workflow(
        self,
        send_notifications: bool = True
    ) -> Dict[str, Any]:
        """
        Run the automated student-mentor matching workflow
        
        Args:
            send_notifications: Whether to send email notifications
            
        Returns:
            dict: Workflow results summary
        """
        results = {
            "students_processed": 0,
            "matches_created": 0,
            "emails_sent": 0,
            "errors": []
        }
        
        try:
            # Get unmatched students
            all_students = self.student_service.get_all_students()
            unmatched_students = []
            
            for student in all_students:
                student_matches = self.match_service.get_student_matches(
                    student.student_id
                )
                if not student_matches:
                    unmatched_students.append(student)
            
            # Get available mentors
            available_mentors = self.mentor_service.get_available_mentors()
            
            if not available_mentors:
                results["errors"].append("No available mentors found")
                return results
            
            # Perform batch matching
            matches = self.matching_engine.batch_match_students(
                unmatched_students,
                available_mentors,
                matches_per_student=3
            )
            
            # Save matches to database
            for match in matches:
                try:
                    match_id = self.match_service.create_match(match)
                    results["matches_created"] += 1
                    
                    # Send notification email if enabled
                    if send_notifications:
                        student = next(
                            (s for s in unmatched_students if s.student_id == match.student_id),
                            None
                        )
                        
                        if student:
                            # Get mentor name from mentor_id
                            mentor = next(
                                (m for m in available_mentors if m.mentor_id == match.mentor_id),
                                None
                            )
                            mentor_name = mentor.name if mentor else "Your Mentor"
                            
                            email_content = self.email_generator.generate_match_notification_email(
                                student.name,
                                mentor_name,
                                match.reason_summary
                            )
                            
                            success, email_id = self.email_service.send_email(
                                recipient_email=student.email,
                                recipient_role="student",
                                subject=email_content["subject"],
                                body=email_content["body"],
                                related_match_id=match_id
                            )
                            
                            if success:
                                results["emails_sent"] += 1
                
                except Exception as e:
                    results["errors"].append(f"Error creating match: {str(e)}")
            
            results["students_processed"] = len(unmatched_students)
            
        except Exception as e:
            results["errors"].append(f"Workflow error: {str(e)}")
        
        return results
    
    def send_welcome_emails_to_new_users(self) -> Dict[str, Any]:
        """
        Send welcome emails to new users who haven't received one
        
        Returns:
            dict: Summary of emails sent
        """
        results = {
            "students_emailed": 0,
            "mentors_emailed": 0,
            "errors": []
        }
        
        try:
            # Get all students
            students = self.student_service.get_all_students()
            
            for student in students:
                try:
                    email_content = self.email_generator.generate_welcome_email(
                        student.name,
                        "student"
                    )
                    
                    success, email_id = self.email_service.send_email(
                        recipient_email=student.email,
                        recipient_role="student",
                        subject=email_content["subject"],
                        body=email_content["body"]
                    )
                    
                    if success:
                        results["students_emailed"] += 1
                
                except Exception as e:
                    results["errors"].append(f"Error emailing student {student.name}: {str(e)}")
            
            # Get all mentors
            mentors = self.mentor_service.get_all_mentors()
            
            for mentor in mentors:
                try:
                    email_content = self.email_generator.generate_welcome_email(
                        mentor.name,
                        "mentor"
                    )
                    
                    success, email_id = self.email_service.send_email(
                        recipient_email=mentor.email,
                        recipient_role="mentor",
                        subject=email_content["subject"],
                        body=email_content["body"]
                    )
                    
                    if success:
                        results["mentors_emailed"] += 1
                
                except Exception as e:
                    results["errors"].append(f"Error emailing mentor {mentor.name}: {str(e)}")
        
        except Exception as e:
            results["errors"].append(f"Workflow error: {str(e)}")
        
        return results
    
    def send_event_announcements(
        self,
        event_id: str,
        target_audience: str = "all"
    ) -> Dict[str, Any]:
        """
        Send event announcements to specified audience
        
        Args:
            event_id: ID of the event
            target_audience: "students", "mentors", or "all"
            
        Returns:
            dict: Summary of emails sent
        """
        results = {
            "emails_sent": 0,
            "errors": []
        }
        
        # Placeholder implementation
        results["errors"].append("Event announcement workflow not yet implemented")
        
        return results
    
    def generate_monthly_summary_report(self) -> str:
        """
        Generate a monthly summary report of platform activity
        
        Returns:
            str: Formatted report text
        """
        try:
            students_count = len(self.student_service.get_all_students())
            mentors_count = len(self.mentor_service.get_all_mentors())
            active_matches = len(self.match_service.get_active_matches())
            pending_matches = len(self.match_service.get_pending_matches())
            
            report = f"""
            CMIS Engagement Platform - Monthly Summary Report
            =================================================
            
            Total Students: {students_count}
            Total Mentors: {mentors_count}
            Active Matches: {active_matches}
            Pending Matches: {pending_matches}
            
            This is an automated report generated by the AI Workflow Engine.
            """
            
            return report.strip()
            
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def run_matching_workflow_for_student(
        self,
        student_id: str,
        top_n: int = 3
    ) -> Dict[str, Any]:
        """
        Run complete matching workflow for a single student.
        Synchronous and safe for Streamlit - no background workers.
        
        Steps:
        1. Load student by ID
        2. Load mentors with available capacity
        3. Rank mentors using AI matching engine
        4. For each top mentor:
           - Generate AI match reason
           - Create MentorMatch entry in database
           - Generate personalized email content via Groq
           - Schedule email for delivery via N8N
        5. Return workflow summary
        
        Args:
            student_id: Student ID to match
            top_n: Number of top mentors to match (default: 3)
            
        Returns:
            dict: Workflow summary with matches created, emails scheduled, errors
        """
        results = {
            "success": False,
            "student_id": student_id,
            "student_name": None,
            "matches_created": 0,
            "emails_scheduled": 0,
            "match_details": [],
            "errors": []
        }
        
        try:
            # Step 1: Load student
            student = self.student_service.get_student_by_id(student_id)
            if not student:
                results["errors"].append(f"Student not found: {student_id}")
                return results
            
            results["student_name"] = student.get("name", "Unknown")
            
            # Step 2: Load mentors with available capacity
            available_mentors = self.mentor_service.get_available_mentors()
            if not available_mentors:
                results["errors"].append("No available mentors found")
                return results
            
            # Step 3: Rank mentors using AI matching engine
            matches = self.matching_engine.find_best_matches(
                student=student,
                available_mentors=available_mentors,
                top_k=top_n,
                include_reasons=True
            )
            
            if not matches:
                results["errors"].append("No matches found")
                return results
            
            # Step 4: Process each match
            for match in matches:
                match_detail = {
                    "mentor_name": match["mentor"].get("name", "Unknown"),
                    "mentor_email": match["mentor"].get("email", "Unknown"),
                    "score": match["score"],
                    "rank": match["rank"],
                    "match_id": None,
                    "email_id": None,
                    "error": None
                }
                
                try:
                    # 4a. Create MentorMatch entry
                    match_data = {
                        "student_id": student_id,
                        "mentor_id": match["mentor"].get("mentor_id"),
                        "match_score": match["score"],
                        "reason_summary": match.get("reason", "AI-generated match"),
                        "status": "pending"
                    }
                    
                    created_match = self.match_service.create_match(match_data)
                    if "error" in created_match:
                        match_detail["error"] = f"Failed to create match: {created_match['error']}"
                        results["errors"].append(match_detail["error"])
                        results["match_details"].append(match_detail)
                        continue
                    
                    match_id = created_match.get("_id")
                    match_detail["match_id"] = match_id
                    results["matches_created"] += 1
                    
                    # 4b. Generate personalized email content via Groq
                    try:
                        subject, body = generate_mentor_outreach_email(
                            student=student,
                            mentor=match["mentor"],
                            match_reason=match.get("reason", "AI-generated match")
                        )
                    except Exception as e:
                        match_detail["error"] = f"Failed to generate email: {str(e)}"
                        results["errors"].append(match_detail["error"])
                        results["match_details"].append(match_detail)
                        continue
                    
                    # 4c. Schedule email for delivery via N8N
                    try:
                        email_log = self.email_service.schedule_email(
                            recipient_email=match["mentor"].get("email"),
                            recipient_role="mentor",
                            subject=subject,
                            body=body,
                            related_match_id=match_id
                        )
                        
                        if "error" in email_log:
                            match_detail["error"] = f"Failed to schedule email: {email_log['error']}"
                            results["errors"].append(match_detail["error"])
                        else:
                            email_id = email_log.get("_id")
                            match_detail["email_id"] = email_id
                            results["emails_scheduled"] += 1
                    except Exception as e:
                        match_detail["error"] = f"Failed to schedule email: {str(e)}"
                        results["errors"].append(match_detail["error"])
                    
                except Exception as e:
                    match_detail["error"] = f"Error processing match: {str(e)}"
                    results["errors"].append(match_detail["error"])
                
                results["match_details"].append(match_detail)
            
            # Mark success if at least one match was created
            if results["matches_created"] > 0:
                results["success"] = True
            
        except Exception as e:
            results["errors"].append(f"Workflow error: {str(e)}")
        
        return results
