# Двухсервисная система LLM-консультаций

## Архитектура
- **Auth Service (FastAPI)** – регистрация, логин и выпуск JWT-токенов.
- **Bot Service (aiogram + FastAPI)** – Telegram-бот с проверкой JWT.
- **Celery + RabbitMQ** – асинхронная обработка запросов к LLM.
- **Redis** – хранение JWT токенов и backend для Celery.

## Пользовательский сценарий
1. Регистрация и получение JWT через Swagger Auth Service.
2. Передача токена боту командой `/token`.
3. Отправка текстового запроса – бот публикует задачу в RabbitMQ.
4. Celery worker обращается к OpenRouter и возвращает ответ пользователю.

## Запуск
```bash
docker compose up -d --build
```

## Контакты

Автор: Щебетовский В.А.
Группа: M25-555