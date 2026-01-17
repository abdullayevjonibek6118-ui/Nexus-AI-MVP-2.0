"""
Тестирование подключения к GigaChat API
Проверяет корректность настройки и получение access token
"""

import sys
import os

# Добавляем backend в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.services.gigachat import gigachat_service
from app.core.config import settings

def test_gigachat_connection():
    """Тестирует подключение к GigaChat API"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ GIGACHAT API")
    print("=" * 60)
    print()
    
    # Проверка конфигурации
    print("1️⃣ Проверка конфигурации...")
    if not settings.GIGACHAT_API_KEY:
        print("   ❌ GIGACHAT_API_KEY не установлен в .env")
        print("   💡 Запустите: python setup_gigachat.py")
        return False
    
    print(f"   ✅ GIGACHAT_API_KEY установлен (длина: {len(settings.GIGACHAT_API_KEY)})")
    print(f"   ✅ GIGACHAT_SCOPE: {settings.GIGACHAT_SCOPE}")
    print(f"   ✅ USE_GIGACHAT: {settings.USE_GIGACHAT}")
    print()
    
    # Тест получения access token
    print("2️⃣ Получение OAuth access token...")
    try:
        token = gigachat_service.get_access_token()
        if token:
            print(f"   ✅ Access token получен успешно")
            print(f"   📝 Токен (первые 20 символов): {token[:20]}...")
        else:
            print("   ❌ Не удалось получить access token")
            print("   💡 Проверьте:")
            print("      - Правильность GIGACHAT_API_KEY в .env")
            print("      - Client ID и Client Secret корректны")
            print("      - Интернет соединение работает")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при получении токена: {e}")
        return False
    print()
    
    # Тест отправки запроса
    print("3️⃣ Тест отправки запроса к GigaChat...")
    try:
        messages = [
            {"role": "system", "content": "Вы - полезный ассистент."},
            {"role": "user", "content": "Привет! Ответь одним предложением."}
        ]
        
        response = gigachat_service.chat_completion(messages, temperature=0.7)
        
        if response:
            print(f"   ✅ Ответ получен успешно")
            print(f"   📝 Ответ ({len(response)} символов):")
            print(f"      {response[:100]}..." if len(response) > 100 else f"      {response}")
        else:
            print("   ❌ Не удалось получить ответ от GigaChat")
            return False
    except Exception as e:
        print(f"   ❌ Ошибка при отправке запроса: {e}")
        return False
    print()
    
    print("=" * 60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)
    print()
    print("🎉 GigaChat API настроен и работает корректно!")
    return True

if __name__ == "__main__":
    success = test_gigachat_connection()
    sys.exit(0 if success else 1)
