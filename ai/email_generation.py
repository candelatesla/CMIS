"""
AI-powered email generation using Groq API
"""
from typing import Optional, Dict
from groq import Groq
from config import GROQ_API_KEY


class EmailGenerator:
    """AI-powered email generator using Groq API"""
    
    def __init__(self, model: str = "llama-3.1-70b-versatile"):
        """
        Initialize the email generator
        
        Args:
            model: Groq model to use (default: llama-3.1-70b-versatile)
                   Options: llama-3.1-70b-versatile, mixtral-8x7b-32768
        """
        self._client = None  # Lazy-load to avoid Groq v0.4.1 proxies issue
        self.model = model
    
    @property
    def client(self):
        """Lazy-load Groq client to avoid initialization issues"""
        if self._client is None:
            self._client = Groq(api_key=GROQ_API_KEY)
        return self._client
    
    def generate_welcome_email(
        self,
        recipient_name: str,
        recipient_type: str = "student"
    ) -> Dict[str, str]:
        """
        Generate a welcome email for new students or mentors
        
        Args:
            recipient_name: Name of the recipient
            recipient_type: Type of recipient ("student" or "mentor")
            
        Returns:
            dict: {"subject": str, "body": str}
        """
        prompt = f"""
        Generate a warm, professional welcome email for a new {recipient_type} joining the CMIS Engagement Platform.
        
        Recipient Name: {recipient_name}
        
        The email should:
        - Welcome them to the program
        - Briefly explain the platform's purpose
        - Mention key features they can use
        - Encourage them to complete their profile
        - Have a friendly, professional tone
        
        Provide the email in the following format:
        SUBJECT: [subject line]
        
        BODY:
        [email body]
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer for an educational mentorship platform."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse subject and body
            parts = content.split("BODY:", 1)
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip() if len(parts) > 1 else content
            
            return {
                "subject": subject_part,
                "body": body
            }
            
        except Exception as e:
            return {
                "subject": f"Welcome to CMIS Engagement Platform!",
                "body": f"Dear {recipient_name},\n\nWelcome to the CMIS Engagement Platform! We're excited to have you join our community.\n\nError generating personalized content: {str(e)}"
            }
    
    def generate_match_notification_email(
        self,
        student_name: str,
        mentor_name: str,
        match_reason: str
    ) -> Dict[str, str]:
        """
        Generate an email notifying about a new match
        
        Args:
            student_name: Name of the student
            mentor_name: Name of the mentor
            match_reason: Reason for the match
            
        Returns:
            dict: {"subject": str, "body": str}
        """
        prompt = f"""
        Generate an email notifying a student about their new mentor match.
        
        Student Name: {student_name}
        Mentor Name: {mentor_name}
        Match Reason: {match_reason}
        
        The email should:
        - Congratulate them on the match
        - Introduce the mentor briefly
        - Explain why they're a good match
        - Provide next steps (accept/reject match)
        - Be encouraging and professional
        
        Provide the email in the following format:
        SUBJECT: [subject line]
        
        BODY:
        [email body]
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional email writer for an educational mentorship platform."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse subject and body
            parts = content.split("BODY:", 1)
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip() if len(parts) > 1 else content
            
            return {
                "subject": subject_part,
                "body": body
            }
            
        except Exception as e:
            return {
                "subject": "New Mentor Match Available!",
                "body": f"Dear {student_name},\n\nWe've matched you with {mentor_name}!\n\n{match_reason}\n\nError generating personalized content: {str(e)}"
            }
    
    def generate_event_announcement(
        self,
        event_title: str,
        event_description: str,
        event_date: str,
        event_location: str
    ) -> Dict[str, str]:
        """
        Generate an event announcement email
        
        Args:
            event_title: Title of the event
            event_description: Description of the event
            event_date: Date and time of the event
            event_location: Location of the event
            
        Returns:
            dict: {"subject": str, "body": str}
        """
        prompt = f"""
        Generate an engaging event announcement email for:
        
        Event: {event_title}
        Description: {event_description}
        Date: {event_date}
        Location: {event_location}
        
        The email should:
        - Create excitement about the event
        - Highlight key benefits of attending
        - Include all important details
        - Encourage registration
        - Be concise and engaging
        
        Provide the email in the following format:
        SUBJECT: [subject line]
        
        BODY:
        [email body]
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional event marketing specialist."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse subject and body
            parts = content.split("BODY:", 1)
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip() if len(parts) > 1 else content
            
            return {
                "subject": subject_part,
                "body": body
            }
            
        except Exception as e:
            return {
                "subject": f"Upcoming Event: {event_title}",
                "body": f"Event: {event_title}\nDate: {event_date}\nLocation: {event_location}\n\n{event_description}\n\nError generating personalized content: {str(e)}"
            }
    
    def generate_custom_email(
        self,
        purpose: str,
        context: str,
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate a custom email based on purpose and context
        
        Args:
            purpose: Purpose of the email
            context: Additional context information
            tone: Desired tone (professional, friendly, formal)
            
        Returns:
            dict: {"subject": str, "body": str}
        """
        prompt = f"""
        Generate an email with the following specifications:
        
        Purpose: {purpose}
        Context: {context}
        Tone: {tone}
        
        Create a well-structured email that achieves the stated purpose.
        
        Provide the email in the following format:
        SUBJECT: [subject line]
        
        BODY:
        [email body]
        """
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional email writer. Write in a {tone} tone."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.7,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            
            # Parse subject and body
            parts = content.split("BODY:", 1)
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip() if len(parts) > 1 else content
            
            return {
                "subject": subject_part,
                "body": body
            }
            
        except Exception as e:
            return {
                "subject": "Important Update",
                "body": f"Error generating email: {str(e)}"
            }


def generate_mentor_outreach_email(
    student: Dict,
    mentor: Dict,
    match_reason: str
) -> tuple[str, str]:
    """
    Generate a personalized mentor outreach email for a student-mentor match.
    
    Args:
        student: Student dictionary with name, major, interests, skills
        mentor: Mentor dictionary with name, job_title, company, expertise_areas
        match_reason: AI-generated reason for the match (should NOT contain scores)
        
    Returns:
        tuple: (subject, body) - email subject and body text (formatted as HTML)
    """
    
    # Import formatting utilities
    from utils.email_formatting import build_mentor_match_email_html, build_mentor_match_email_plain
    
    # Extract student and mentor information for subject line
    student_name = student.get('name', 'Student')
    mentor_name = mentor.get('name', 'Mentor')
    
    # Try to generate AI-powered content for subject
    subject = f"Mentorship Opportunity: {student_name}"
    
    try:
        from groq import Groq as GroqClient
        client = GroqClient(api_key=GROQ_API_KEY)
        
        # Quick prompt just for subject line
        subject_prompt = f"Write a warm, brief subject line (max 60 chars) for an email introducing {student_name} to mentor {mentor_name}. Just the subject line, no extra text."
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You write brief, warm email subject lines. Output only the subject line, nothing else."
                },
                {
                    "role": "user",
                    "content": subject_prompt
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.6,
            max_tokens=50,
            top_p=0.9
        )
        
        ai_subject = response.choices[0].message.content.strip()
        # Clean up any quotation marks or extra formatting
        ai_subject = ai_subject.replace('"', '').replace("'", "").replace('SUBJECT:', '').strip()
        if len(ai_subject) <= 80 and ai_subject:
            subject = ai_subject
        
    except Exception as e:
        print(f"Note: Using fallback subject line (AI generation not available: {str(e)})")
    
    # Use HTML formatting by default
    body = build_mentor_match_email_html(student, mentor, match_reason)
    
    return (subject, body)
