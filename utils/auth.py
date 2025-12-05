"""
Authentication utilities for CMIS Admin Dashboard
"""
import os
from typing import Tuple, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def load_admin_credentials() -> Tuple[List[str], str]:
    """
    Load admin credentials from environment variables
    
    Returns:
        tuple: (list of admin emails, admin password)
    """
    admin_emails_str = os.getenv("ADMIN_EMAILS", "")
    admin_password = os.getenv("ADMIN_PASSWORD", "")
    
    # Parse comma-separated emails
    admin_emails = [email.strip() for email in admin_emails_str.split(",") if email.strip()]
    
    return admin_emails, admin_password


def check_login(email: str, password: str) -> bool:
    """
    Validate admin login credentials
    
    Args:
        email: Email address to check
        password: Password to verify
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    admin_emails, admin_password = load_admin_credentials()
    
    # Check if email is in the admin list and password matches
    email_valid = email.strip().lower() in [e.lower() for e in admin_emails]
    password_valid = password == admin_password
    
    return email_valid and password_valid
