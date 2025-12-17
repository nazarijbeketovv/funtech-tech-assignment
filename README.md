# Order Service

Сервис управления заказами на FastAPI с JWT-аутентификацией, кешированием в Redis, очередями сообщений (RabbitMQ) и фоновой обработкой задач (Celery).

## Возможности

- Регистрация и аутентификация пользователей (JWT)
- Создание и управление заказами
- Кеширование заказов в Redis (TTL 5 минут)
- Публикация событий в RabbitMQ при создании заказа
- Фоновая обработка заказов через Celery
- Rate limiting и CORS защита

## Быстрый старт

1. Скопируйте файл с переменными окружения:
```bash
make env
```

2. Запустите приложение:
```bash
make app
```

Приложение будет доступно по адресу `http://localhost:8000`

## Тестирование API

### Через Swagger UI

Откройте в браузере: `http://localhost:8000/docs`

### Через curl

#### 1. Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

#### 2. Получение JWT токена
```bash
curl -X POST "http://localhost:8000/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

Сохраните полученный `access_token` в переменную:
```bash
TOKEN="ваш_токен_здесь"
```

#### 3. Создание заказа
```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "items": [
      {"name": "Товар 1", "quantity": 2, "price": 100.50},
      {"name": "Товар 2", "quantity": 1, "price": 250.00}
    ],
    "total_price": 451.00
  }'
```

Сохраните `id` заказа:
```bash
ORDER_ID="uuid_заказа_здесь"
```

#### 4. Получение заказа
```bash
curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

#### 5. Обновление статуса заказа
```bash
curl -X PATCH "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "PAID"}'
```

Доступные статусы: `PENDING`, `PAID`, `SHIPPED`, `CANCELED`

#### 6. Получение списка заказов пользователя
```bash
USER_ID=1
curl -X GET "http://localhost:8000/orders/user/$USER_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

## Проверка работы компонентов

### RabbitMQ Management UI
Откройте `http://localhost:15672` (логин: `guest`, пароль: `guest`)

### Логи сервисов
```bash
# Логи API
docker compose logs api

# Логи consumer (обработка событий из RabbitMQ)
docker compose logs consumer

# Логи Celery worker (фоновая обработка заказов)
docker compose logs celery_worker
```

## Технологии

- FastAPI, Pydantic
- PostgreSQL, SQLAlchemy, Alembic
- Redis (кеширование, rate limiting)
- RabbitMQ (очереди сообщений)
- Celery (фоновая обработка задач)
