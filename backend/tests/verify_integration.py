"""
Quick verification script to test OpenRouter API and DeepSeek model integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.openrouter import analyze_resume
from app.services.resume_parser import parse_resume
from app.core.config import settings


def test_openrouter_api():
    """Test OpenRouter API with DeepSeek model."""
    print("=" * 60)
    print("Testing OpenRouter API with DeepSeek Model")
    print("=" * 60)
    
    vacancy_desc = """
    Позиция: Python Backend Developer
    
    Требования:
    - Опыт работы с Python 3+ лет
    - Знание FastAPI или Django
    - Опыт работы с PostgreSQL
    - Понимание REST API
    - Опыт с Docker
    
    Будет плюсом:
    - Знание Kubernetes
    - Опыт с облачными сервисами (AWS/GCP)
    """
    
    resume_text = """
    Иван Петров
    Python Developer
    
    Опыт работы: 4 года
    
    Навыки:
    - Python, FastAPI, Django
    - PostgreSQL, MongoDB
    - Docker, Git
    - REST API разработка
    
    Предыдущие проекты:
    - Разработка микросервисной архитектуры на FastAPI
    - Оптимизация работы с БД PostgreSQL
    - Интеграция сторонних API
    """
    
    try:
        print("\n📊 Analyzing resume...")
        print(f"Model: {settings.AI_MODEL_NAME}")
        print(f"API Key configured: {'Yes' if settings.OPENROUTER_API_KEY else 'No'}")
        
        result = analyze_resume(
            vacancy_description=vacancy_desc,
            resume_text=resume_text
        )
        
        print(f"\n✅ Analysis successful!")
        print(f"\n📈 Score: {result.score * 100:.0f}%")
        print(f"📝 Recommendation: {result.recommendation}")
        print(f"✔️  Matched Skills: {', '.join(result.skills_match)}")
        print(f"❌ Missing Skills: {', '.join(result.missing_skills)}")
        print(f"\n💬 Screening Questions ({len(result.screening_questions)}):")
        for i, q in enumerate(result.screening_questions, 1):
            print(f"   {i}. {q}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_resume_parser():
    """Test resume parser functions."""
    print("\n" + "=" * 60)
    print("Testing Resume Parser")
    print("=" * 60)
    
    # Test TXT parsing
    txt_content = b"Test Resume Content\nName: John Doe\nSkills: Python, FastAPI"
    result = parse_resume("resume.txt", txt_content)
    print(f"\n✔️  TXT parsing: {result[:50]}...")
    
    print("\n✅ Resume parser tests passed")
    return True


def test_config():
    """Test configuration."""
    print("\n" + "=" * 60)
    print("Testing Configuration")
    print("=" * 60)
    
    print(f"\n✔️  AI Model: {settings.AI_MODEL_NAME}")
    print(f"✔️  OpenRouter API Key: {settings.OPENROUTER_API_KEY[:20]}...")
    print(f"✔️  Database URL: {settings.DATABASE_URL}")
    print(f"✔️  HH Client ID: {settings.HH_CLIENT_ID[:20] if settings.HH_CLIENT_ID else 'Not set'}...")
    
    return True


if __name__ == "__main__":
    print("\n🚀 Nexus AI Verification Script\n")
    
    results = []
    
    # Test 1: Configuration
    results.append(("Configuration", test_config()))
    
    # Test 2: Resume Parser
    results.append(("Resume Parser", test_resume_parser()))
    
    # Test 3: OpenRouter API
    results.append(("OpenRouter + DeepSeek", test_openrouter_api()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
    
    sys.exit(0 if all_passed else 1)
