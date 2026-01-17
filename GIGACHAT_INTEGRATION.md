# 🤖 Интеграция GigaChat API - Руководство

## Обзор

GigaChat - это AI модель от Сбербанка для работы на русском языке. Сервис интегрирован в Nexus AI и работает параллельно с OpenRouter.

---

## Получение API Ключа

### Шаг 1: Регистрация
1. Перейдите на https://developers.sber.ru/studio/
2. Зарегистрируйтесь или войдите
3. Создайте новый проект

### Шаг 2: Получение Credentials
1. В личном кабинете создайте "Авторизационные данные"
2. Выберите scope: `GIGACHAT_API_PERS` (персональный доступ)
3. Скопируйте Client ID и Client Secret

**Текущие данные:**
- **Client ID:** `019b9dbd-68f9-7cb0-a899-792120ee2477`
- **Scope:** `GIGACHAT_API_PERS`

4. Конвертируйте в Base64:
   ```python
   import base64
   credentials = f"{client_id}:{client_secret}"
   api_key = base64.b64encode(credentials.encode()).decode()
   print(api_key)
   ```
   
   Или используйте утилиту:
   ```bash
   python setup_gigachat.py
   ```

### Шаг 3: Настройка в .env
```env
# GigaChat (Sber)
GIGACHAT_API_KEY="ваш-base64-ключ-здесь"
USE_GIGACHAT=true  # Включить GigaChat
```

---

## Архитектура

### Компоненты

1. **GigaChatService** (`backend/app/services/gigachat.py`)
   - OAuth аутентификация
   - Получение access token
   - Chat completion requests
   - Анализ кандидатов

2. **Chat API** (`backend/app/api/chat.py`)
   - Интеграция GigaChat + OpenRouter
   - Автоматический fallback
   - Хранение истории в БД

3. **Config** (`backend/app/core/config.py`)
   - `GIGACHAT_API_KEY`
   - `GIGACHAT_SCOPE`
   - `USE_GIGACHAT`

---

## Использование

### Включение GigaChat

В файле `.env` установите:
```env
USE_GIGACHAT=true
```

### Приоритет AI моделей

1. **GigaChat** (если `USE_GIGACHAT=true` и ключ настроен)
2. **OpenRouter/DeepSeek** (fallback)

### Пример запроса

```python
from app.services.gigachat import get_gigachat_response

messages = [
    {"role": "system", "content": "Вы - HR ассистент"},
    {"role": "user", "content": "Привет! Расскажите о себе"}
]

response = get_gigachat_response(messages, temperature=0.7)
print(response)
```

---

## Хранение Истории Чата

### База Данных

История чата **автоматически сохраняется** в таблице `chat_messages`:

```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER NOT NULL,
    role VARCHAR,  -- 'user' или 'assistant'
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### API Endpoints

**GET** `/api/chat/{candidate_id}`
- Получить всю историю чата с кандидатом
- Сообщения отсортированы по времени создания

**POST** `/api/chat/`
```json
{
  "candidate_id": 1,
  "role": "user",
  "content": "Привет, расскажите о себе"
}
```
- Автоматически сохраняет сообщение
- Генерирует AI ответ (GigaChat или OpenRouter)
- Сохраняет AI ответ в историю

### Просмотр История на Frontend

В `candidate-view.html` секция чата автоматически:
1. Загружает историю при открытии карточки
2. Отображает все сообщения (user + assistant)
3. Сохраняет новые сообщения в БД
4. Обновляет интерфейс после ответа AI

---

## Тестирование

### Проверка GigaChat подключения

**Быстрый тест:**
```bash
python test_gigachat.py
```

**Или вручную:**
```bash
cd backend
python -c "from app.services.gigachat import gigachat_service; token = gigachat_service.get_access_token(); print('Token:', token[:20] if token else 'Failed')"
```

### Тест чата

```bash
python
```

```python
from app.services.gigachat import get_gigachat_response

messages = [
    {"role": "system", "content": "Вы - HR ассистент"},
    {"role": "user", "content": "Привет!"}
]

response = get_gigachat_response(messages)
print(response)
```

---

## Сравнение: GigaChat vs OpenRouter

| Характеристика | GigaChat | OpenRouter/DeepSeek |
|----------------|----------|---------------------|
| **Язык** | Русский (native) | Многоязычная |
| **Latency** | ~2-3 сек | ~3-5 сек |
| **Стоимость** | Бесплатно (лимиты) | Бесплатно (лимиты) |
| **Качество (RU)** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **API** | Требует OAuth | Простой Bearer token |
| **SSL** | Самоподписанный | Стандартный |

---

## Troubleshooting

### Ошибка: "401 Unauthorized"
**Причина:** Истёк access token или неверный API key

**Решение:**
1. Переполучите credentials на https://developers.sber.ru/studio/
2. Пересоздайте Base64 ключ
3. Обновите `GIGACHAT_API_KEY` в `.env`
4. Перезапустите backend

### Ошибка: "SSL Certificate verify failed"
**Причина:** У GigaChat самоподписанный сертификат

**Решение:** Отключено в коде через `verify=False` (только для разработки)

### Fallback к OpenRouter
**Поведение:** Если GigaChat не отвечает, автоматически используется OpenRouter

**Логи:**
```
⚠️ GigaChat error, fallback to OpenRouter: <error>
✅ Использован OpenRouter для ответа
```

---

## Production Considerations

### SSL Сертификаты

Для production добавьте сертификаты Сбера:
```python
import certifi

response = requests.post(
    url,
    verify=certifi.where(),  # Вместо verify=False
    ...
)
```

### Rate Limiting

GigaChat имеет лимиты:
- **Бесплатный тариф:** ~1000 запросов/день
- **Коммерческий:** Без лимитов

Мониторьте usage на https://developers.sber.ru

### Monitoring

Добавьте логирование:
```python
import logging

logger = logging.getLogger("gigachat")
logger.info(f"Request to GigaChat: {len(messages)} messages")
logger.error(f"GigaChat API error: {response.status_code}")
```

---

## Безопасность

### Защита API Key

- ✅ Хранится в `.env` (не в Git)
- ✅ Base64 encoding
- ✅ Только backend имеет доступ
- ⚠️ В production используйте secrets management (Vault, AWS Secrets)

### Валидация

```python
if not settings.GIGACHAT_API_KEY or len(settings.GIGACHAT_API_KEY) < 20:
    raise ValueError("Invalid GIGACHAT_API_KEY")
```

---

## Документация API

### GigaChat OAuth

**POST** `https://ngw.devices.sberbank.ru:9443/api/v2/oauth`

Headers:
```
Authorization: Basic <base64_credentials>
Content-Type: application/x-www-form-urlencoded
RqUID: <uuid>
```

Body:
```
scope=GIGACHAT_API_PERS
```

Response:
```json
{
  "access_token": "eyJhbGciOiJS...",
  "expires_at": 1673456789
}
```

### GigaChat Chat Completion

**POST** `https://gigachat.devices.sberbank.ru/api/v1/chat/completions`

Headers:
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

Body:
```json
{
  "model": "GigaChat",
  "messages": [
    {"role": "system", "content": "Вы - ассистент"},
    {"role": "user", "content": "Привет!"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

---

## Ссылки

- **Документация:** https://developers.sber.ru/docs/ru/gigachat/api/overview
- **Личный кабинет:** https://developers.sber.ru/studio/
- **Поддержка:** dev@sberbank.ru

---

**Дата обновления:** 08.01.2026  
**Версия:** 1.0
