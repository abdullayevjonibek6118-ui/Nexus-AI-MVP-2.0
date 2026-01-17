"""
GigaChat API Integration Service
Provides AI chat functionality using Sber's GigaChat
"""

import requests
import uuid
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GigaChatService:
    """Service для работы с GigaChat API"""
    
    def __init__(self):
        self.oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.access_token = None
        
    def get_access_token(self) -> Optional[str]:
        """
        Получение OAuth токена для GigaChat API
        """
        try:
            payload = {
                'scope': settings.GIGACHAT_SCOPE
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4()),
                'Authorization': f'Basic {settings.GIGACHAT_API_KEY}'
            }
            
            response = requests.post(
                self.oauth_url,
                headers=headers,
                data=payload,
                verify=False,  # SSL сертификаты Sber
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                logger.info("✅ GigaChat: Access token получен")
                return self.access_token
            else:
                logger.error(f"❌ GigaChat OAuth error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ GigaChat OAuth exception: {str(e)}")
            return None
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Optional[str]:
        """
        Отправка запроса в GigaChat для генерации ответа
        
        Args:
            messages: Список сообщений в формате [{"role": "user", "content": "текст"}]
            temperature: Температура генерации (0.0 - 1.0)
            max_tokens: Максимальное количество токенов в ответе
            
        Returns:
            Текст ответа от GigaChat или None при ошибке
        """
        try:
            # Получаем токен, если его нет
            if not self.access_token:
                if not self.get_access_token():
                    return None
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.access_token}'
            }
            
            payload = {
                'model': 'GigaChat',  # Название модели
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'n': 1
            }
            
            response = requests.post(
                self.chat_url,
                headers=headers,
                json=payload,
                verify=False,  # SSL сертификаты Sber
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    content = data['choices'][0]['message']['content']
                    logger.info(f"✅ GigaChat: Ответ получен ({len(content)} символов)")
                    return content
                else:
                    logger.error("❌ GigaChat: Некорректный формат ответа")
                    return None
                    
            elif response.status_code == 401:
                # Токен истёк, получаем новый и повторяем
                logger.warning("⚠️ GigaChat: Токен истёк, получаем новый...")
                self.access_token = None
                if self.get_access_token():
                    return self.chat_completion(messages, temperature, max_tokens)
                return None
                
            else:
                logger.error(f"❌ GigaChat API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ GigaChat exception: {str(e)}")
            return None
    
    def analyze_candidate(
        self,
        vacancy_description: str,
        resume_text: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Анализ кандидата с помощью GigaChat
        
        Args:
            vacancy_description: Описание вакансии
            resume_text: Текст резюме кандидата
            system_prompt: Кастомный системный промпт
            
        Returns:
            Словарь с результатами анализа
        """
        default_prompt = """Вы - опытный HR-специалист. Проанализируйте резюме кандидата относительно вакансии и предоставьте:
1. Оценку соответствия от 0 до 100
2. Список совпадающих навыков
3. Список недостающих навыков
4. Общую рекомендацию (Strong hire / Hire / Maybe / No hire)
5. 3-5 конкретных вопросов для собеседования на русском языке

Ответьте в формате JSON."""
        
        prompt_to_use = system_prompt or default_prompt
        
        messages = [
            {
                "role": "system",
                "content": prompt_to_use
            },
            {
                "role": "user",
                "content": f"Вакансия:\n{vacancy_description}\n\nРезюме кандидата:\n{resume_text}"
            }
        ]
        
        response_text = self.chat_completion(messages, temperature=0.7)
        
        if not response_text:
            return {
                "error": "Не удалось получить ответ от GigaChat",
                "score": 0,
                "recommendation": "No hire"
            }
        
        # Попытка парсинга JSON или возврат текстового ответа
        try:
            import json
            import re
            
            # Ищем JSON в ответе, включая возможные markdown блоки
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"⚠️ GigaChat: Ошибка парсинга JSON: {e}")
            pass
        
        # Если JSON не распарсился, возвращаем текстовый ответ
        return {
            "raw_response": response_text,
            "score": 0,  
            "recommendation": "Требуется ручная проверка",
            "error": "Не удалось корректно распознать JSON формат ответа"
        }


# Singleton instance
gigachat_service = GigaChatService()


def get_gigachat_response(
    messages: List[Dict[str, str]],
    temperature: float = 0.7
) -> Optional[str]:
    """
    Удобная функция для получения ответа от GigaChat
    """
    return gigachat_service.chat_completion(messages, temperature)
