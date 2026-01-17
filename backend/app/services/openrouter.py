
import json
import requests
import re
from app.core.config import settings
from app.schemas.candidate import CandidateAnalysisResult

def analyze_resume(vacancy_description: str, resume_text: str, 
                   system_prompt: str = None, 
                   model: str = "x-ai/grok-4.1-fast", 
                   temperature: float = 0.7) -> CandidateAnalysisResult:
    """
    Analyzes resume using OpenRouter API with configurable settings.
    """
    
    # Default system prompt if none provided
    if not system_prompt:
        system_prompt = """You are an expert HR AI assistant specializing in candidate screening and resume analysis. 
Your role is to objectively evaluate candidates against job requirements and provide actionable insights."""
    
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
    Do not add markdown formatting, just the raw JSON string.
    """

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": settings.PROJECT_NAME,
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model, 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        
        result_json = response.json()
        content = result_json["choices"][0]["message"]["content"]
        
        # Cleanup
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        data = json.loads(content.strip())
        return CandidateAnalysisResult(**data)

    except Exception as e:
        print(f"OpenRouter API Error: {e}")
        # Fallback
        return CandidateAnalysisResult(
            score=0.0,
            skills_match=[],
            missing_skills=[],
            summary=f"Error analyzing resume: {str(e)}",
            recommendation="Review manually"
        )
