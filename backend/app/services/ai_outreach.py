
from app.services.openrouter import analyze_resume
from app.core.config import settings

class AIOutreachService:
    def generate_message(self, candidate_name: str, vacancy_title: str, skills: list, model: str = None) -> str:
        """
        Generates a personalized outreach message using AI.
        """
        
        skills_str = ", ".join(skills) if skills else "ваш профессиональный опыт"
        
        prompt = f"""
        Напиши вежливое и персонализированное письмо-приглашение кандидату на вакансию.
        
        Имя кандидата: {candidate_name}
        Вакансия: {vacancy_title}
        Ключевые навыки кандидата: {skills_str}
        
        Письмо должно быть:
        - Коротким (не более 100 слов)
        - Дружелюбным, но профессиональным
        - Упоминать конкретные навыки кандидата
        - Заканчиваться призывом к ответу (например, "Когда вам удобно созвониться?")
        
        Верни ТОЛЬКО текст письма, без лишних комментариев.
        """
        
        # Call the generic completion method
        from app.services.openrouter import generate_completion
        
        try:
            message = generate_completion(
                prompt=prompt,
                system_prompt="You are a professional HR assistant helping to recruit candidates.",
                model=model,
                temperature=0.7
            )
            # Remove any quotes if AI adds them
            return message.strip('"').strip("'")
        except Exception as e:
             # Fallback to template if error
             print(f"AI Outreach Error: {e}")
             return f"Здравствуйте, {candidate_name}!\n\nМеня впечатлил ваш опыт, особенно владение {skills_str}. Мы ищем специалиста на позицию {vacancy_title}.\n\nКогда вам удобно обсудить детали?\n\nС уважением,\nКоманда Nexus AI"

ai_outreach_service = AIOutreachService()
