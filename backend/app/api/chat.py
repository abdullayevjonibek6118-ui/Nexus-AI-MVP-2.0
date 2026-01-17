from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.chat import ChatMessage
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ChatMessageSchema(BaseModel):
    id: int
    candidate_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessageCreate(BaseModel):
    candidate_id: int
    role: str
    content: str

@router.get("/{candidate_id}", response_model=List[ChatMessageSchema])
def get_chat_history(
    candidate_id: int,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """Получить историю чата с кандидатом (хранится в БД)"""
    messages = db.query(ChatMessage).filter(
        ChatMessage.candidate_id == candidate_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return messages

@router.post("/", response_model=ChatMessageSchema)
def create_chat_message(
    msg: ChatMessageCreate,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    Отправить сообщение в чат.
    """
    is_init = msg.content == "AI_START"
    
    if not is_init:
        # Сохранить сообщение (пользователя или ассистента)
        db_msg = ChatMessage(
            candidate_id=msg.candidate_id,
            role=msg.role,
            content=msg.content
        )
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
    else:
        # Если это инициация, создаем фиктивное сообщение для возврата, 
        # но оно будет перезаписано ответом AI ниже
        db_msg = ChatMessage(id=0, candidate_id=msg.candidate_id, role='assistant', content='AI thinking...', created_at=datetime.utcnow())

    # Генерировать ответ AI если роль user или это инициация
    if msg.role == 'user' or is_init:
        from app.models.candidate import Candidate
        from app.models.vacancy import Vacancy
        from app.core.config import settings
        
        # Получить контекст кандидата и вакансии
        candidate = db.query(Candidate).filter(Candidate.id == msg.candidate_id).first()
        if candidate:
            vacancy = db.query(Vacancy).filter(Vacancy.id == candidate.vacancy_id).first()
            
            # Построить контекст для AI
            context = f"""Вакансия: {vacancy.title if vacancy else 'N/A'}
Описание: {vacancy.description[:300] if vacancy else 'N/A'}...
Зарплата: {vacancy.salary_range if vacancy and vacancy.salary_range else 'Не указана'}
Веса навыков (Skill Weights): {vacancy.skill_weights if vacancy and vacancy.skill_weights else 'Standard'}

Резюме кандидата: {candidate.summary or candidate.content[:500]}...

Ранее заданные вопросы скрининга:
"""
            if candidate.screening_questions:
                for i, q in enumerate(candidate.screening_questions[:3], 1):
                    context += f"{i}. {q}\n"
            
            # Подготовить сообщения для AI
            system_message = """Вы - экспертный HR AI ассистент. 
Ваши цели в этом чате:
1. Уточнить готовность кандидата к конкретным условиям вакансии (з/п, график, задачи).
2. Провести "Technical/Skill Check" - задайте точечный вопрос по одному из навыков, заявленных в резюме, чтобы убедиться в компетенции.
3. Оцените мотивацию.

Будьте вежливы, но профессионально-критичны. Ориентируйтесь на веса навыков (Skill Weights) - чем выше вес, тем важнее этот навык проверить. Общайтесь только на русском языке."""

            user_prompt = f"""{context}

Сообщение от кандидата: {msg.content}

Действуйте как HR AI. Проанализируйте ответ. Если это начало чата - поприветствуйте и уточните готовность к требованиям вакансии. Если чат продолжается - проведите мини-проверку заявленных навыков. Дайте лаконичный, человечный ответ."""
            
            # Fetch AI Settings for current user
            from app.models.ai_settings import AISettings
            ai_settings = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
            
            selected_model = ai_settings.model_name if ai_settings else settings.AI_MODEL_NAME
            ai_temp = ai_settings.temperature if ai_settings else 0.7
            
            ai_content = None
            
            # Try GigaChat if explicitly selected or if global toggle is ON
            if (selected_model == "GigaChat" or settings.USE_GIGACHAT) and settings.GIGACHAT_API_KEY:
                try:
                    from app.services.gigachat import get_gigachat_response
                    
                    messages = [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_prompt}
                    ]
                    
                    ai_content = get_gigachat_response(messages, temperature=ai_temp)
                    
                    if ai_content:
                        print(f"✅ Использован GigaChat для ответа (модель: {selected_model})")
                except Exception as e:
                    print(f"⚠️ GigaChat error, fallback to OpenRouter: {e}")
            
            # Fallback to OpenRouter or default model
            if not ai_content and settings.OPENROUTER_API_KEY:
                # If GigaChat was failed but selected, we fallback to DeepSeek
                fallback_model = selected_model if selected_model != "GigaChat" else settings.AI_MODEL_NAME
                try:
                    import requests
                    
                    response = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": fallback_model,
                            "messages": [
                                {"role": "system", "content": system_message},
                                {"role": "user", "content": user_prompt}
                            ],
                            "temperature": ai_temp
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        ai_content = response.json()["choices"][0]["message"]["content"]
                        print("✅ Использован OpenRouter для ответа")
                    else:
                        print(f"❌ OpenRouter error: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ OpenRouter exception: {e}")
            
            # Сохранить ответ AI если сгенерирован
            if ai_content:
                ai_msg = ChatMessage(
                    candidate_id=msg.candidate_id,
                    role='assistant',
                    content=ai_content
                )
                db.add(ai_msg)
                db.commit()
                if is_init:
                    db_msg = ai_msg
                print(f"💾 История чата сохранена в БД (candidate_id={msg.candidate_id})")
    
    return db_msg


class HRAskSchema(BaseModel):
    candidate_id: int
    question: str

@router.post("/hr_ask", response_model=str)
def ask_hr_helper(
    req: HRAskSchema,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_active_user),
):
    """
    HR спрашивает AI о кандидате или навыках.
    Ответ возвращается строкой (не сохраняется в основной истории чата, чтобы не смешивать).
    """
    from app.models.candidate import Candidate
    from app.models.vacancy import Vacancy
    from app.core.config import settings

    candidate = db.query(Candidate).filter(Candidate.id == req.candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    vacancy = db.query(Vacancy).filter(Vacancy.id == candidate.vacancy_id).first()

    context = f"""Вакансия: {vacancy.title if vacancy else 'N/A'}
Описание: {vacancy.description[:500] if vacancy else 'N/A'}...
Зарплата: {vacancy.salary_range if vacancy and vacancy.salary_range else 'Не указана'}
Требуемые навыки: {vacancy.required_skills if vacancy else 'N/A'}

Кандидат: {candidate.filename}
Резюме: {candidate.summary or candidate.content[:1000]}...
Skills Match: {candidate.skills_match}
Missing Skills: {candidate.missing_skills}
"""

    system_message = "Вы - эксперт HR-аналитик. Рекрутер задает вам вопросы о кандидате. Дайте честный, развернутый и полезный ответ на русском языке. Используйте метрики и факты из резюме."
    user_prompt = f"""Контекст:
{context}

Вопрос рекрутера: {req.question}

Ответ:"""

    # Model selection (reuse logic or simplify for this endpoint)
    # Using simple openrouter fallback logic for brevity/consistency
    from app.models.ai_settings import AISettings
    import requests

    ai_settings = db.query(AISettings).filter(AISettings.user_id == current_user.id).first()
    model = ai_settings.model_name if ai_settings else settings.AI_MODEL_NAME
    temp = 0.7

    content = "Извините, AI сейчас недоступен."

    # Try GigaChat
    if (model == "GigaChat" or settings.USE_GIGACHAT) and settings.GIGACHAT_API_KEY:
        try:
            from app.services.gigachat import get_gigachat_response
            msgs = [{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}]
            content = get_gigachat_response(msgs, temperature=temp) or content
        except Exception as e:
            print(f"HR GigaChat fail: {e}")

    # Fallback OpenRouter
    if content == "Извините, AI сейчас недоступен." and settings.OPENROUTER_API_KEY:
        try:
             response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"},
                json={
                    "model": model if model != "GigaChat" else settings.AI_MODEL_NAME,
                    "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": user_prompt}],
                    "temperature": temp
                },
                timeout=45
            )
             if response.status_code == 200:
                 content = response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"HR OpenRouter fail: {e}")

    return content
