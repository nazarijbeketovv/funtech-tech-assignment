# Тестовые запросы для проверки API

Базовый URL: `http://localhost:8000`

## 1. Регистрация пользователя

```bash
curl -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

**Ожидаемый результат:** HTTP 201, JSON с `id`, `email`, `created_at`

---

## 2. Получение JWT токена (OAuth2)

```bash
curl -X POST "http://localhost:8000/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

**Ожидаемый результат:** HTTP 200, JSON с `access_token` и `token_type: "bearer"`

**Сохраните токен в переменную:**
```bash
TOKEN="ваш_токен_здесь"
```

---

## 3. Создание заказа (требует авторизации)

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

**Ожидаемый результат:** HTTP 201, JSON с созданным заказом (сохраните `id` заказа)

**Сохраните ID заказа:**
```bash
ORDER_ID="uuid_заказа_здесь"
```

---

## 4. Получение заказа по ID (проверка кеширования Redis)

### Первый запрос (из БД):
```bash
curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

### Второй запрос (должен быть из Redis кеша):
```bash
curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

**Ожидаемый результат:** HTTP 200, JSON с данными заказа

**Проверка:** В логах должно быть видно, что второй запрос берёт данные из кеша (TTL = 5 минут)

---

## 5. Обновление статуса заказа

```bash
curl -X PATCH "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "status": "PAID"
  }'
```

**Ожидаемый результат:** HTTP 200, JSON с обновлённым заказом

**Проверка:** После обновления кеш должен обновиться

**Дополнительные статусы для тестирования:**
```bash
# SHIPPED
curl -X PATCH "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "SHIPPED"}'

# CANCELED
curl -X PATCH "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "CANCELED"}'
```

---

## 6. Получение списка заказов пользователя

```bash
# Сначала получите user_id из ответа регистрации или токена
USER_ID=1

curl -X GET "http://localhost:8000/orders/user/$USER_ID/" \
  -H "Authorization: Bearer $TOKEN"
```

**Ожидаемый результат:** HTTP 200, JSON массив с заказами пользователя

---

## 7. Тестирование защиты эндпоинтов

### Попытка создать заказ без токена:
```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{"name": "Товар", "quantity": 1, "price": 100.00}],
    "total_price": 100.00
  }'
```

**Ожидаемый результат:** HTTP 401 Unauthorized

### Попытка получить заказ с невалидным токеном:
```bash
curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Authorization: Bearer invalid_token_here"
```

**Ожидаемый результат:** HTTP 401 Unauthorized

### Попытка получить заказы другого пользователя:
```bash
# Создайте второго пользователя и получите его токен, затем:
curl -X GET "http://localhost:8000/orders/user/1/" \
  -H "Authorization: Bearer $TOKEN_USER2"
```

**Ожидаемый результат:** HTTP 403 Forbidden (если user_id не совпадает с текущим пользователем)

---

## 8. Тестирование Rate Limiting

Выполните более 30 запросов в минуту (значение из настроек):

```bash
for i in {1..35}; do
  curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
    -H "Authorization: Bearer $TOKEN"
  echo "Request $i"
done
```

**Ожидаемый результат:** После 30 запросов должен вернуться HTTP 429 Too Many Requests

---

## 9. Тестирование валидации данных

### Регистрация с некорректным email:
```bash
curl -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "password": "password123"
  }'
```

**Ожидаемый результат:** HTTP 422 Validation Error

### Регистрация с коротким паролем:
```bash
curl -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test2@example.com",
    "password": "12345"
  }'
```

**Ожидаемый результат:** HTTP 422 Validation Error (пароль должен быть минимум 6 символов)

### Создание заказа с отрицательной ценой:
```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "items": [{"name": "Товар", "quantity": 1, "price": 100.00}],
    "total_price": -10.00
  }'
```

**Ожидаемый результат:** HTTP 422 Validation Error

### Создание заказа с пустым списком товаров:
```bash
curl -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "items": [],
    "total_price": 100.00
  }'
```

**Ожидаемый результат:** HTTP 422 Validation Error

---

## 10. Тестирование получения несуществующего заказа

```bash
curl -X GET "http://localhost:8000/orders/00000000-0000-0000-0000-000000000000/" \
  -H "Authorization: Bearer $TOKEN"
```

**Ожидаемый результат:** HTTP 404 Not Found

---

## 11. Проверка работы RabbitMQ и Celery

После создания заказа проверьте логи:

```bash
# Логи consumer (должен получить событие new_order)
docker compose logs consumer

# Логи celery_worker (должна выполниться фоновая задача)
docker compose logs celery_worker
```

**Ожидаемое поведение:**
1. При создании заказа событие публикуется в RabbitMQ
2. Consumer получает событие и передаёт в Celery
3. Celery worker обрабатывает задачу (time.sleep(2) и print)

---

## 12. Проверка Swagger UI

Откройте в браузере:
```
http://localhost:8000/docs
```

**Проверка:**
- Все эндпоинты отображаются
- Можно выполнить запросы через UI
- Схемы данных корректны
- Есть описание эндпоинтов

---

## 13. Проверка CORS

```bash
curl -X OPTIONS "http://localhost:8000/orders/" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**Ожидаемый результат:** В заголовках ответа должны быть `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers`

---

## Полный сценарий тестирования (последовательно)

```bash
# 1. Регистрация
REGISTER_RESPONSE=$(curl -s -X POST "http://localhost:8000/register/" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}')
echo "Registration: $REGISTER_RESPONSE"

# 2. Получение токена
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123")
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 3. Создание заказа
ORDER_RESPONSE=$(curl -s -X POST "http://localhost:8000/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"items": [{"name": "Товар 1", "quantity": 2, "price": 100.50}], "total_price": 201.00}')
ORDER_ID=$(echo $ORDER_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "Order ID: $ORDER_ID"

# 4. Получение заказа (первый раз - из БД)
curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Authorization: Bearer $TOKEN"

# 5. Получение заказа (второй раз - из кеша)
curl -X GET "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Authorization: Bearer $TOKEN"

# 6. Обновление статуса
curl -X PATCH "http://localhost:8000/orders/$ORDER_ID/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"status": "PAID"}'

# 7. Получение списка заказов
curl -X GET "http://localhost:8000/orders/user/1/" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Что проверить в логах после прогона:

1. **API логи** - проверка обработки запросов, ошибок
2. **Consumer логи** - получение событий из RabbitMQ
3. **Celery worker логи** - выполнение фоновых задач
4. **Redis логи** - операции кеширования
5. **PostgreSQL логи** - SQL запросы (должны быть только ORM, без SQL-инъекций)
