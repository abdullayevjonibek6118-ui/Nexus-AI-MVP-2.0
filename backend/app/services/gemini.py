
import json
import google.generativeai as genai
from app.core.config import settings
from app.schemas.candidate import CandidateAnalysisResult

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def analyze_resume(vacancy_description: str, resume_text: str) -> CandidateAnalysisResult:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    You are an expert HR AI assistant. Your job is to screen a candidate's resume against a vacancy description.
    
    Vacancy Description:
    {vacancy_description}
    
    Resume Text:
    {resume_text}
    
    Analyze the resume and provide:
    1. A match score from 0.0 to 1.0 (float).
    2. List of matching skills found in the resume.
    3. List of missing skills that are required but not found.
    4. A brief professional summary of the candidate (max 2 sentences).
    5. A recommendation (e.g., "Strong hire", "Interview", "Reject").
    
    Output strictly in Valid JSON format with the following structure:
    {{
        "score": float,
        "skills_match": ["skill1", "skill2"],
        "missing_skills": ["skill3"],
        "summary": "text...",
        "recommendation": "text..."
    }}
    Do not add markdown formatting like ```json ... ```, just the raw JSON string.
    """
    
    try:
        response = model.generate_content(prompt)
        # Cleanup potential markdown ticks if Gemini adds them
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        data = json.loads(text.strip())
        return CandidateAnalysisResult(**data)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Fallback for testing or error
        return CandidateAnalysisResult(
            score=0.0,
            skills_match=[],
            missing_skills=[],
            summary="Error analyzing resume.",
            recommendation="Review manually"
        )
