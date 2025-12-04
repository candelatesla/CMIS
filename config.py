"""
Configuration module for CMIS Engagement Platform
Loads environment variables for MongoDB, Groq API, and N8N webhook
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "cmis_engagement")

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# N8N Webhook Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

# Application Settings
APP_TITLE = "CMIS Engagement Platform Admin Dashboard"
APP_VERSION = "1.0.0"

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = {
        "MONGODB_URI": MONGODB_URI,
        "GROQ_API_KEY": GROQ_API_KEY,
        "N8N_WEBHOOK_URL": N8N_WEBHOOK_URL
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print(f"Warning: Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the required variables.")
    
    return len(missing_vars) == 0
