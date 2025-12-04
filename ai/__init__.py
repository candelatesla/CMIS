"""
AI package for CMIS Engagement Platform
Includes matching algorithms, email generation, and workflow automation
"""
from .matching import MatchingEngine
from .email_generation import EmailGenerator
from .workflow import WorkflowEngine

__all__ = [
    "MatchingEngine",
    "EmailGenerator",
    "WorkflowEngine"
]
