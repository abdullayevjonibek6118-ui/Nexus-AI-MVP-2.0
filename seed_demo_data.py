import os
import sys

# Force DATABASE_URL for seeding to point to the backend database
# Must be DONE BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite:///backend/sql_app.db"

sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.db.session import SessionLocal
import app.db.base  # Register all models!
from app.models.vacancy import Vacancy
from app.models.candidate import Candidate
from app.models.chat import ChatMessage
from app.models.user import User
import json

def seed():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No user found. Run create_user_root.py first.")
            return

        # 1. Create a demo vacancy if not exists
        vacancy = db.query(Vacancy).filter(Vacancy.title == "Senior Python Developer (Demo)").first()
        if not vacancy:
            vacancy = Vacancy(
                title="Senior Python Developer (Demo)",
                description="We are looking for a senior developer with experience in FastAPI and LLM integration.",
                required_skills="Python, FastAPI, SQL, OpenAI/Anthropic/Gemini",
                experience_level="Senior",
                salary_range="300k-500k",
                owner_id=user.id
            )
            db.add(vacancy)
            db.commit()
            db.refresh(vacancy)
            print(f"Created vacancy: {vacancy.id}")
        
        # 2. Add Candidate 1 (Good Match)
        c1 = db.query(Candidate).filter(Candidate.filename == "alex_python_dev.pdf").first()
        if not c1:
            c1 = Candidate(
                vacancy_id=vacancy.id,
                filename="alex_python_dev.pdf",
                content="Alex is a senior dev with 8 years of Python experience, specialized in backend and AI.",
                score=0.92,
                skills_match=["Python", "FastAPI", "SQL"],
                missing_skills=["Gemini"],
                summary="Highly qualified candidate with strong backend background.",
                recommendation="Strongly Recommend",
                status="SHORTLIST"
            )
            db.add(c1)
            print("Added Alex")

        # 3. Add Candidate 2 (Middle Match)
        c2 = db.query(Candidate).filter(Candidate.filename == "maria_data_scientist.pdf").first()
        if not c2:
            c2 = Candidate(
                vacancy_id=vacancy.id,
                filename="maria_data_scientist.pdf",
                content="Maria is a data scientist with Python knowledge but less web dev experience.",
                score=0.55,
                skills_match=["Python"],
                missing_skills=["FastAPI", "SQL"],
                summary="Good Python skills, but lacks specific web framework experience.",
                recommendation="Consider for data roles",
                status="NEW"
            )
            db.add(c2)
            print("Added Maria")

        db.commit()
        db.refresh(c1)
        db.refresh(c2)

        # 4. Add Chat History for Alex
        if not db.query(ChatMessage).filter(ChatMessage.candidate_id == c1.id).first():
            messages = [
                ("assistant", "Здравствуйте, Алексей! Ваш профиль отлично подходит под вакансию. Когда вам удобно созвониться?"),
                ("user", "Добрый день! Спасибо за отзыв. Могу завтра в 11:00."),
                ("assistant", "Договорились, завтра в 11:00 отправлю ссылку на Zoom.")
            ]
            for role, content in messages:
                db.add(ChatMessage(candidate_id=c1.id, role=role, content=content))
            print("Added chat for Alex")

        # 5. Add Chat History for Maria
        if not db.query(ChatMessage).filter(ChatMessage.candidate_id == c2.id).first():
            messages = [
                ("assistant", "Мария, добрый день! Спасибо за отклик. Расскажите подробнее о вашем опыте с FastAPI?"),
                ("user", "Здравствуйте! У меня не так много опыта с FastAPI, в основном использовала Python для анализа данных.")
            ]
            for role, content in messages:
                db.add(ChatMessage(candidate_id=c2.id, role=role, content=content))
            print("Added chat for Maria")

        db.commit()
        print("Seeding complete.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
