
import json
import requests
import re
from app.core.config import settings
from app.schemas.candidate import CandidateAnalysisResult

def analyze_resume(vacancy_description: str, resume_text: str, 
                   system_prompt: str = None, 
                   model: str = None, 
                   temperature: float = 0.7) -> CandidateAnalysisResult:
    """
    Analyzes resume using OpenRouter API with configurable settings.
    Default model is DeepSeek v3.1 (nex-agi/deepseek-v3.1-nex-n1:free).
    """
    
    # Handle GigaChat
    if model == "GigaChat" or (settings.USE_GIGACHAT and settings.GIGACHAT_API_KEY):
        try:
            from app.services.gigachat import gigachat_service
            analysis = gigachat_service.analyze_candidate(vacancy_description, resume_text, system_prompt)
            
            # Ensure all required fields are present for CandidateAnalysisResult
            return CandidateAnalysisResult(
                score=float(analysis.get("score", 0.7)),
                skills_match=analysis.get("skills_match", []),
                missing_skills=analysis.get("missing_skills", []),
                summary=analysis.get("summary", "Resume analysis completed via GigaChat."),
                recommendation=analysis.get("recommendation", "Consider for interview"),
                screening_questions=analysis.get("screening_questions", ["Расскажите подробнее о вашем опыте работы?"])
            )
        except Exception as e:
            print(f"GigaChat Analysis Error: {e}")
            # Fallback will continue to OpenRouter below
            model = 'nex-agi/deepseek-v3.1-nex-n1:free'
    
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
    6. 3-5 specific screening questions based strictly on their resume and the job requirements. 
    These should be realistic HR-style questions (in the language of the vacancy/resume, likely Russian) that help verify their experience or clarify points in their resume.

    Output strictly in Valid JSON format with the following structure:
    {{
        "score": float,
        "skills_match": ["skill1", "skill2"],
        "missing_skills": ["skill3"],
        "summary": "text...",
        "recommendation": "text...",
        "screening_questions": ["question1", "question2", ...]
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
            score=0.85,
            skills_match=["Python", "FastAPI", "SQL"],
            missing_skills=["Cloud Ops"],
            summary=f"Analysis placeholder (API Error: {str(e)}). This is a mock result for demonstration.",
            recommendation="Interview",
            screening_questions=[
                "В вашем резюме указан опыт работы с Python. Можете ли вы подробнее рассказать о самом сложном проекте, где вы использовали FastAPI?",
                "Как вы подходите к оптимизации SQL-запросов в приложениях с высокой нагрузкой?",
                "В вакансии требуется опыт работы с облачными технологиями, который неявно указан в резюме. Был ли у вас такой опыт?"
            ]
        )

def generate_completion(prompt: str, system_prompt: str = None, 
                        model: str = None, 
                        temperature: float = 0.7) -> str:
    """
    Generic completion method that supports both OpenRouter and GigaChat.
    """
    if model is None:
        model = getattr(settings, 'AI_MODEL_NAME', 'nex-agi/deepseek-v3.1-nex-n1:free')
        
    # Handle GigaChat
    if model == "GigaChat" or (settings.USE_GIGACHAT and settings.GIGACHAT_API_KEY):
        try:
            from app.services.gigachat import get_gigachat_response
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = get_gigachat_response(messages, temperature=temperature)
            if response:
                return response
        except Exception as e:
            print(f"GigaChat Completion Error: {e}")
            model = 'nex-agi/deepseek-v3.1-nex-n1:free'

    # OpenRouter
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": model, 
        "messages": messages,
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
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenRouter Completion Error: {e}")
        return "Извините, произошла ошибка при генерации сообщения."
