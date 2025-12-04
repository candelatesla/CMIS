"""
PDF processing utilities for extracting text from resumes
"""
import pdfplumber
from typing import Optional
import io
import random
import os


def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """
    Extract text content from a PDF file (standalone function)
    
    Args:
        pdf_file: File-like object or path to PDF file
        
    Returns:
        str: Extracted text or None if error
    """
    try:
        # Handle different input types
        if isinstance(pdf_file, str):
            # File path
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text.strip()
        else:
            # File-like object (e.g., from Streamlit file uploader)
            with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text.strip()
    
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        return None


class PDFProcessor:
    """Utility class for processing PDF files"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_file) -> Optional[str]:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_file: File-like object or path to PDF file
            
        Returns:
            str: Extracted text or None if error
        """
        return extract_text_from_pdf(pdf_file)
    
    @staticmethod
    def extract_text_from_multiple_pdfs(pdf_files: list) -> dict:
        """
        Extract text from multiple PDF files
        
        Args:
            pdf_files: List of PDF file objects or paths
            
        Returns:
            dict: Mapping of filename to extracted text
        """
        results = {}
        
        for pdf_file in pdf_files:
            filename = getattr(pdf_file, 'name', 'unknown.pdf')
            text = PDFProcessor.extract_text_from_pdf(pdf_file)
            results[filename] = text
        
        return results
    
    @staticmethod
    def extract_resume_sections(text: str) -> dict:
        """
        Extract common sections from resume text (basic implementation)
        
        Args:
            text: Resume text
            
        Returns:
            dict: Dictionary with identified sections
        """
        # This is a basic implementation
        # In production, you might want to use more sophisticated NLP techniques
        sections = {
            "education": "",
            "experience": "",
            "skills": "",
            "full_text": text
        }
        
        text_lower = text.lower()
        
        # Try to identify common section headers
        if "education" in text_lower:
            sections["has_education"] = True
        
        if "experience" in text_lower or "work history" in text_lower:
            sections["has_experience"] = True
        
        if "skills" in text_lower or "technical skills" in text_lower:
            sections["has_skills"] = True
        
        return sections
    
    @staticmethod
    def validate_pdf(pdf_file) -> bool:
        """
        Validate that a file is a readable PDF
        
        Args:
            pdf_file: File object to validate
            
        Returns:
            bool: True if valid PDF, False otherwise
        """
        try:
            if isinstance(pdf_file, str):
                with pdfplumber.open(pdf_file) as pdf:
                    return len(pdf.pages) > 0
            else:
                with pdfplumber.open(io.BytesIO(pdf_file.read())) as pdf:
                    return len(pdf.pages) > 0
        except Exception:
            return False


def get_random_student_resume() -> str:
    """
    Get a random sample student resume from the sample data
    
    Returns:
        str: Random student resume text
    """
    try:
        # Get the path to sample_data directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sample_file = os.path.join(current_dir, 'sample_data', 'sample_student_resumes.txt')
        
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by separator (assuming resumes are separated by "---" or blank lines)
        resumes = [r.strip() for r in content.split('\n---\n') if r.strip()]
        
        if not resumes:
            # Fallback if no separator found
            return content.strip()
        
        return random.choice(resumes)
    
    except Exception as e:
        print(f"Error loading sample student resume: {str(e)}")
        return "Sample student resume not available"


def get_random_mentor_resume() -> str:
    """
    Get a random sample mentor resume from the sample data
    
    Returns:
        str: Random mentor resume text
    """
    try:
        # Get the path to sample_data directory
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sample_file = os.path.join(current_dir, 'sample_data', 'sample_mentor_resumes.txt')
        
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by separator
        resumes = [r.strip() for r in content.split('\n---\n') if r.strip()]
        
        if not resumes:
            # Fallback if no separator found
            return content.strip()
        
        return random.choice(resumes)
    
    except Exception as e:
        print(f"Error loading sample mentor resume: {str(e)}")
        return "Sample mentor resume not available"
