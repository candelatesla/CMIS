"""
AI-powered matching engine for student-mentor pairing
Uses Groq API with Mixtral for intelligent matching and explanations
"""
from typing import List, Dict, Tuple, Any
from groq import Groq
import json
import re


# Groq API Configuration
GROQ_API_KEY = "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"


def compute_match_score(student: Dict[str, Any], mentor: Dict[str, Any]) -> float:
    """
    Compute hybrid match score between student and mentor
    
    Scoring breakdown:
    - 40% = overlap between student.interests and mentor.expertise_areas
    - 40% = overlap between student.skills and mentor.expertise_areas  
    - 20% = text similarity between student.resume_text and mentor.resume_text
    
    Args:
        student: Student dictionary with interests, skills, resume_text
        mentor: Mentor dictionary with expertise_areas, resume_text
        
    Returns:
        float: Match score between 0.0 and 1.0
    """
    # Extract fields with defaults
    student_interests = student.get('interests', [])
    student_skills = student.get('skills', [])
    student_resume = student.get('resume_text', '')
    
    mentor_expertise = mentor.get('expertise_areas', [])
    mentor_resume = mentor.get('resume_text', '')
    
    # Normalize to lowercase for comparison
    student_interests_lower = [i.lower() for i in student_interests]
    student_skills_lower = [s.lower() for s in student_skills]
    mentor_expertise_lower = [e.lower() for e in mentor_expertise]
    
    # 1. Interest-Expertise Overlap (40%)
    interest_overlap = 0.0
    if student_interests_lower and mentor_expertise_lower:
        # Count matching items
        matches = sum(1 for interest in student_interests_lower 
                     if any(interest in exp or exp in interest 
                           for exp in mentor_expertise_lower))
        interest_overlap = matches / max(len(student_interests_lower), len(mentor_expertise_lower))
    
    # 2. Skills-Expertise Overlap (40%)
    skills_overlap = 0.0
    if student_skills_lower and mentor_expertise_lower:
        # Count matching items
        matches = sum(1 for skill in student_skills_lower 
                     if any(skill in exp or exp in skill 
                           for exp in mentor_expertise_lower))
        skills_overlap = matches / max(len(student_skills_lower), len(mentor_expertise_lower))
    
    # 3. Resume Text Similarity (20%) - Keyword overlap fallback
    resume_similarity = 0.0
    if student_resume and mentor_resume:
        # Extract keywords (alphanumeric words, lowercase)
        student_keywords = set(re.findall(r'\b[a-z]{3,}\b', student_resume.lower()))
        mentor_keywords = set(re.findall(r'\b[a-z]{3,}\b', mentor_resume.lower()))
        
        # Remove common stopwords
        stopwords = {'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 
                    'been', 'are', 'was', 'were', 'will', 'can', 'about', 'into'}
        student_keywords = student_keywords - stopwords
        mentor_keywords = mentor_keywords - stopwords
        
        if student_keywords and mentor_keywords:
            # Jaccard similarity
            intersection = len(student_keywords & mentor_keywords)
            union = len(student_keywords | mentor_keywords)
            resume_similarity = intersection / union if union > 0 else 0.0
    
    # Compute weighted score
    final_score = (
        0.40 * interest_overlap +
        0.40 * skills_overlap +
        0.20 * resume_similarity
    )
    
    # Ensure score is between 0 and 1
    return max(0.0, min(1.0, final_score))


def rank_mentors_for_student(
    student: Dict[str, Any], 
    mentors: List[Dict[str, Any]], 
    top_n: int = 5
) -> List[Dict[str, Any]]:
    """
    Rank mentors for a student and return top N matches
    
    Args:
        student: Student dictionary
        mentors: List of mentor dictionaries
        top_n: Number of top matches to return
        
    Returns:
        List of dictionaries with mentor, score, and rank
    """
    # Compute scores for all mentors
    scored_mentors = []
    for mentor in mentors:
        score = compute_match_score(student, mentor)
        scored_mentors.append({
            'mentor': mentor,
            'score': score,
            'mentor_name': mentor.get('name', 'Unknown'),
            'mentor_id': mentor.get('mentor_id', 'N/A')
        })
    
    # Sort by score descending
    scored_mentors.sort(key=lambda x: x['score'], reverse=True)
    
    # Add rank
    for idx, item in enumerate(scored_mentors[:top_n], start=1):
        item['rank'] = idx
    
    return scored_mentors[:top_n]


def generate_match_reason(
    student: Dict[str, Any], 
    mentor: Dict[str, Any], 
    score: float
) -> str:
    """
    Use Groq LLM (Mixtral) to generate explanation for why student and mentor match
    
    Args:
        student: Student dictionary
        mentor: Mentor dictionary
        score: Match score (0.0 to 1.0)
        
    Returns:
        str: 2-3 sentence explanation of the match
    """
    try:
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Prepare context
        student_name = student.get('name', 'Student')
        student_major = student.get('major', 'N/A')
        student_interests = ', '.join(student.get('interests', [])[:5])
        student_skills = ', '.join(student.get('skills', [])[:5])
        
        mentor_name = mentor.get('name', 'Mentor')
        mentor_title = mentor.get('job_title', 'N/A')
        mentor_company = mentor.get('company', 'N/A')
        mentor_expertise = ', '.join(mentor.get('expertise_areas', [])[:6])
        
        # Create prompt
        prompt = f"""Generate a brief, professional explanation (2-3 sentences) for why this student-mentor pairing is a strong match.

Student: {student_name}
Major: {student_major}
Interests: {student_interests}
Skills: {student_skills}

Mentor: {mentor_name}
Title: {mentor_title} at {mentor_company}
Expertise: {mentor_expertise}

Match Score: {score:.2f} (out of 1.0)

Write a concise, encouraging explanation focusing on skill alignment and career growth opportunities. Be specific about what makes this match valuable."""
        
        # Call Groq API with Mixtral
        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert career advisor explaining student-mentor matches. Write clear, professional, and encouraging explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=200,
            top_p=0.9
        )
        
        # Extract response
        reason = completion.choices[0].message.content.strip()
        
        # Clean up any markdown or extra formatting
        reason = reason.replace('**', '').replace('*', '')
        
        return reason
        
    except Exception as e:
        # Fallback explanation if API fails
        return f"{student.get('name', 'The student')} and {mentor.get('name', 'this mentor')} show strong alignment in their professional interests and expertise areas, with a match score of {score:.2f}. This mentorship offers valuable opportunities for career development and skill enhancement."


class MatchingEngine:
    """AI-powered matching engine using Groq API"""
    
    def __init__(self, model: str = "mixtral-8x7b-32768"):
        """
        Initialize the matching engine
        
        Args:
            model: Groq model to use (default: mixtral-8x7b-32768)
        """
        self.model = model
        self._client = None  # Lazy initialization
    
    @property
    def client(self):
        """Lazy initialization of Groq client"""
        if self._client is None:
            try:
                self._client = Groq(api_key=GROQ_API_KEY)
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
                # Client will be created fresh in each method call if needed
        return self._client
    
    def compute_match_score(self, student: Dict[str, Any], mentor: Dict[str, Any]) -> float:
        """
        Compute hybrid match score (wrapper for module function)
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            
        Returns:
            float: Match score between 0.0 and 1.0
        """
        return compute_match_score(student, mentor)
    
    def rank_mentors_for_student(
        self, 
        student: Dict[str, Any], 
        mentors: List[Dict[str, Any]], 
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rank mentors for a student (wrapper for module function)
        
        Args:
            student: Student dictionary
            mentors: List of mentor dictionaries
            top_n: Number of top matches to return
            
        Returns:
            List of ranked mentor matches
        """
        return rank_mentors_for_student(student, mentors, top_n)
    
    def generate_match_reason(
        self, 
        student: Dict[str, Any], 
        mentor: Dict[str, Any], 
        score: float
    ) -> str:
        """
        Generate match explanation (wrapper for module function)
        
        Args:
            student: Student dictionary
            mentor: Mentor dictionary
            score: Match score
            
        Returns:
            str: Explanation text
        """
        return generate_match_reason(student, mentor, score)
    
    def find_best_matches(
        self,
        student: Dict[str, Any],
        available_mentors: List[Dict[str, Any]],
        top_k: int = 5,
        include_reasons: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Find the best mentor matches for a student with scores and explanations
        
        Args:
            student: Student dictionary
            available_mentors: List of available mentor dictionaries
            top_k: Number of top matches to return
            include_reasons: Whether to generate AI explanations
            
        Returns:
            List of match dictionaries with mentor, score, rank, and reason
        """
        # Get ranked matches
        ranked_matches = self.rank_mentors_for_student(student, available_mentors, top_k)
        
        # Add AI-generated reasons if requested
        if include_reasons:
            for match in ranked_matches:
                match['reason'] = self.generate_match_reason(
                    student, 
                    match['mentor'], 
                    match['score']
                )
        
        return ranked_matches

