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
        match_reason: AI-generated reason for the match
        
    Returns:
        tuple: (subject, body) - email subject and body text
    """
    
    # Extract student information
    student_name = student.get('name', 'Student')
    student_major = student.get('major', 'N/A')
    student_grad_year = student.get('grad_year', 'N/A')
    student_interests = ', '.join(student.get('interests', [])[:4])
    student_skills = ', '.join(student.get('skills', [])[:6])
    
    # Extract mentor information
    mentor_name = mentor.get('name', 'Mentor')
    mentor_title = mentor.get('job_title', 'N/A')
    mentor_company = mentor.get('company', 'N/A')
    mentor_expertise = ', '.join(mentor.get('expertise_areas', [])[:5])
    
    # Create the prompt
    prompt = f"""Write a warm, personalized outreach email from a CMIS coordinator to a mentor about mentoring a specific student.

STUDENT DETAILS:
- Name: {student_name}
- Major: {student_major}
- Graduation Year: {student_grad_year}
- Interests: {student_interests}
- Skills: {student_skills}

MENTOR DETAILS:
- Name: {mentor_name}
- Title: {mentor_title} at {mentor_company}
- Expertise: {mentor_expertise}

MATCH REASON:
{match_reason}

REQUIREMENTS:
1. Write in a warm, human, conversational tone (as if from a real CMIS coordinator)
2. Be highly specific - mention actual skills, interests, and expertise areas
3. Explain why this particular student would benefit from this particular mentor
4. Make it personal, not generic or templated
5. Keep it concise (3-4 short paragraphs)
6. End with: "Would you be open to mentoring this student?"
7. Sign off as "The CMIS Team"

Provide the email in this format:
SUBJECT: [compelling subject line]

BODY:
[email body]"""
    
    # Create Groq client inside the try block to handle initialization gracefully
    subject_part = None
    body = None
    
    try:
        from groq import Groq as GroqClient
        client = GroqClient(api_key=GROQ_API_KEY)
        
        # Call Groq API with Mixtral
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a CMIS coordinator writing highly personalized outreach emails to mentors. Avoid generic phrasing. Be warm, human, and specific to the individuals involved."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=500,
            top_p=0.9
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse subject and body
        if "BODY:" in content:
            parts = content.split("BODY:", 1)
            subject_part = parts[0].replace("SUBJECT:", "").strip()
            body = parts[1].strip()
        else:
            # Fallback parsing
            lines = content.split('\n', 1)
            subject_part = lines[0].replace("SUBJECT:", "").strip()
            body = lines[1].strip() if len(lines) > 1 else content
        
        # Clean up any markdown or extra formatting
        subject_part = subject_part.replace('**', '').replace('*', '')
        body = body.replace('**', '').replace('*', '')
        
        return (subject_part, body)
        
    except Exception as e:
        # Fallback email in case of API error (works with Groq v0.4.1 compatibility issues)
        subject = f"Mentorship Opportunity: {student_name}"
        body = f"""Hi {mentor_name},

I hope this email finds you well. I'm reaching out from the CMIS Engagement Platform to introduce you to {student_name}, a {student_major} major graduating in {student_grad_year}.

{match_reason}

Given your expertise in {mentor_expertise} and {student_name}'s interests in {student_interests}, I believe this could be a valuable mentorship connection for both of you.

Would you be open to mentoring this student?

Best regards,
The CMIS Team"""
        
        return (subject, body)
