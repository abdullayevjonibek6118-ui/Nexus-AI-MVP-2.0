"""
Утилита для настройки GigaChat API
Генерирует Base64 ключ из Client ID и Client Secret
"""

import base64
import os
from pathlib import Path

def generate_gigachat_key(client_id: str, client_secret: str) -> str:
    """
    Генерирует Base64 ключ для GigaChat API
    
    Args:
        client_id: Client ID от GigaChat
        client_secret: Client Secret от GigaChat
        
    Returns:
        Base64 закодированная строка для использования в Authorization header
    """
    credentials = f"{client_id}:{client_secret}"
    api_key = base64.b64encode(credentials.encode()).decode()
    return api_key

def update_env_file(api_key: str, use_gigachat: bool = True):
    """
    Обновляет или создает .env файл с настройками GigaChat
    
    Args:
        api_key: Base64 ключ для GigaChat
        use_gigachat: Включить ли GigaChat по умолчанию
    """
    env_path = Path("backend/.env")
    if not env_path.exists():
        env_path = Path(".env")
    
    # Читаем существующий .env или создаем новый
    env_content = ""
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            env_content = f.read()
    
    # Обновляем или добавляем GigaChat настройки
    lines = env_content.split("\n")
    updated_lines = []
    gigachat_key_found = False
    use_gigachat_found = False
    
    for line in lines:
        if line.startswith("GIGACHAT_API_KEY="):
            updated_lines.append(f'GIGACHAT_API_KEY="{api_key}"')
            gigachat_key_found = True
        elif line.startswith("USE_GIGACHAT="):
            updated_lines.append(f"USE_GIGACHAT={str(use_gigachat).lower()}")
            use_gigachat_found = True
        else:
            updated_lines.append(line)
    
    # Добавляем если не найдено
    if not gigachat_key_found:
        updated_lines.append(f'GIGACHAT_API_KEY="{api_key}"')
    if not use_gigachat_found:
        updated_lines.append(f"USE_GIGACHAT={str(use_gigachat).lower()}")
    
    # Записываем обратно
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(updated_lines))
    
    print(f"✅ Настройки GigaChat обновлены в {env_path}")
    print(f"   GIGACHAT_API_KEY установлен")
    print(f"   USE_GIGACHAT={use_gigachat}")

def main():
    """Интерактивная настройка GigaChat"""
    print("=" * 60)
    print("🔧 НАСТРОЙКА GIGACHAT API")
    print("=" * 60)
    print()
    
    # Предоставленные данные
    client_id = "019b9dbd-68f9-7cb0-a899-792120ee2477"
    scope = "GIGACHAT_API_PERS"
    
    print(f"Client ID: {client_id}")
    print(f"Scope: {scope}")
    print()
    
    # Запрашиваем Client Secret
    print("⚠️  Для генерации Base64 ключа нужен Client Secret")
    print("   Если ключ уже сгенерирован и находится в .env, нажмите Enter")
    print()
    
    client_secret = input("Введите Client Secret (или Enter для пропуска): ").strip()
    
    if client_secret:
        # Генерируем ключ
        api_key = generate_gigachat_key(client_id, client_secret)
        print()
        print("✅ Base64 ключ сгенерирован:")
        print(f"   {api_key}")
        print()
        
        # Обновляем .env
        use_gigachat_input = input("Включить GigaChat по умолчанию? (y/n, по умолчанию y): ").strip().lower()
        use_gigachat = use_gigachat_input != "n"
        
        update_env_file(api_key, use_gigachat)
        print()
        print("✅ Настройка завершена!")
        print()
        print("📝 Следующие шаги:")
        print("   1. Перезапустите backend сервер")
        print("   2. Проверьте подключение: python test_gigachat.py")
    else:
        print()
        print("ℹ️  Пропущено. Убедитесь, что GIGACHAT_API_KEY установлен в .env")
        print()
        print("📝 Формат в .env:")
        print('   GIGACHAT_API_KEY="ваш-base64-ключ-здесь"')
        print("   USE_GIGACHAT=true")

if __name__ == "__main__":
    main()
