"""
Email Formatting Utilities
Reusable functions for formatting mentor outreach and team registration emails
"""


def build_mentor_match_email_plain(student: dict, mentor: dict, match_reason: str) -> str:
    """
    Build plain text mentor match email
    
    Args:
        student: Student dictionary with name, major, grad_year, etc.
        mentor: Mentor dictionary with name, company, job_title, etc.
        match_reason: Explanation of why they were matched
        
    Returns:
        Formatted plain text email body
    """
    student_name = student.get('name', 'Student')
    student_major = student.get('major', 'N/A')
    student_grad_year = student.get('grad_year', 'N/A')
    student_interests = ', '.join(student.get('interests', [])[:3]) or 'N/A'
    
    mentor_name = mentor.get('name', 'Mentor')
    
    body = f"""Howdy {mentor_name},

You have been identified as a strong match for mentoring the following student:

Student: {student_name}
Major: {student_major}
Graduation Year: {student_grad_year}
Interests: {student_interests}

Why you were matched:
{match_reason.strip()}

If you are open to connecting with this student, please reply to this email and our CMIS team will help coordinate the introduction.

Best regards,
CMIS Engagement Platform
Texas A&M University"""
    
    return body.strip()


def build_mentor_match_email_html(student: dict, mentor: dict, match_reason: str) -> str:
    """
    Build HTML mentor match email
    
    Args:
        student: Student dictionary with name, major, grad_year, etc.
        mentor: Mentor dictionary with name, company, job_title, etc.
        match_reason: Explanation of why they were matched
        
    Returns:
        Formatted HTML email body
    """
    student_name = student.get('name', 'Student')
    student_major = student.get('major', 'N/A')
    student_grad_year = student.get('grad_year', 'N/A')
    student_interests = ', '.join(student.get('interests', [])[:3]) or 'N/A'
    
    mentor_name = mentor.get('name', 'Mentor')
    
    # Clean up match reason - replace newlines with <br> for HTML
    match_reason_html = match_reason.strip().replace('\n', '<br>')
    
    html = f"""<p>Howdy {mentor_name},</p>

<p>You have been identified as a strong match for mentoring the following student:</p>

<h3>Student Details</h3>
<ul>
  <li><strong>Name:</strong> {student_name}</li>
  <li><strong>Major:</strong> {student_major}</li>
  <li><strong>Graduation Year:</strong> {student_grad_year}</li>
  <li><strong>Interests:</strong> {student_interests}</li>
</ul>

<h3>Why You Were Matched</h3>
<p>{match_reason_html}</p>

<p>If you are open to connecting, please reply to this email and our team will coordinate the introduction.</p>

<p>Best regards,<br>
<strong>CMIS Engagement Platform</strong><br>
Texas A&M University</p>"""
    
    return html.strip()


def build_team_registration_email_plain(
    member_name: str,
    event_name: str,
    event_date: str,
    team_name: str,
    all_members: list
) -> tuple[str, str]:
    """
    Build plain text team registration email
    
    Args:
        member_name: Name of the team member
        event_name: Name of the event
        event_date: Date of the event
        team_name: Name of the team
        all_members: List of all team member names
        
    Returns:
        tuple: (subject, body)
    """
    subject = f"CMIS Competition Registration – {event_name} – Team {team_name}"
    
    members_list = "\n".join([f"  • {member}" for member in all_members])
    
    body = f"""Dear {member_name},

Congratulations! You have been successfully registered for the CMIS competition.

Event Details:
  • Event: {event_name}
  • Date: {event_date}
  • Team Name: {team_name}

Your Team Members:
{members_list}

You are now officially registered in the CMIS Engagement Platform. We look forward to seeing your team compete!

If you have any questions, please don't hesitate to reach out to the CMIS team.

Best regards,
CMIS Engagement Platform
Texas A&M University"""
    
    return subject, body.strip()


def build_team_registration_email_html(
    member_name: str,
    event_name: str,
    event_date: str,
    team_name: str,
    all_members: list
) -> tuple[str, str]:
    """
    Build HTML team registration email
    
    Args:
        member_name: Name of the team member
        event_name: Name of the event
        event_date: Date of the event
        team_name: Name of the team
        all_members: List of all team member names
        
    Returns:
        tuple: (subject, body)
    """
    subject = f"CMIS Competition Registration – {event_name} – Team {team_name}"
    
    members_html = "\n".join([f"  <li>{member}</li>" for member in all_members])
    
    html = f"""<p>Dear {member_name},</p>

<p>Congratulations! You have been successfully registered for the CMIS competition.</p>

<h3>Event Details</h3>
<ul>
  <li><strong>Event:</strong> {event_name}</li>
  <li><strong>Date:</strong> {event_date}</li>
  <li><strong>Team Name:</strong> {team_name}</li>
</ul>

<h3>Your Team Members</h3>
<ul>
{members_html}
</ul>

<p>You are now officially registered in the CMIS Engagement Platform. We look forward to seeing your team compete!</p>

<p>If you have any questions, please don't hesitate to reach out to the CMIS team.</p>

<p>Best regards,<br>
<strong>CMIS Engagement Platform</strong><br>
Texas A&M University</p>"""
    
    return subject, html.strip()
