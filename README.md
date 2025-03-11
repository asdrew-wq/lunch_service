# Lunch Service

Lunch Service — це API для вибору закладу харчування із підтримкою версіонування (v1.0 та v2.0). Проєкт побудований на Django та Django REST Framework, використовує PostgreSQL як базу даних і розгортається через Docker Compose.

## Вимоги

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Python 3.13.1 (встановлюється автоматично в контейнері)

### Залежності
Проєкт використовує наступні Python-пакети, які вказані в `requirements.txt` і встановлюються автоматично під час побудови Docker-образу:
```python
asgiref==3.8.1
Django==5.1.7
djangorestframework==3.15.2
djangorestframework_simplejwt==5.5.0
flake8==7.1.2
iniconfig==2.0.0
mccabe==0.7.0
packaging==24.2
pluggy==1.5.0
psycopg2-binary==2.9.10
pycodestyle==2.12.1
pyflakes==3.2.0
PyJWT==2.9.0
pytest==8.3.5
pytest-django==4.10.0
sqlparse==0.5.3
```

- **Django**: Основний фреймворк.
- **djangorestframework**: Для створення REST API.
- **djangorestframework_simplejwt**: JWT-авторизація.
- **psycopg2-binary**: Драйвер для PostgreSQL.
- **pytest** та **pytest-django**: Для запуску тестів.
- **flake8**: Для перевірки стилю коду.

## Як запустити систему

### 1. Клонування репозиторію
Склонуйте репозиторій на свій локальний комп’ютер:

```bash
git clone https://github.com/yourusername/lunch_service.git
cd lunch_service
```
Замініть yourusername на свій GitHub-нікнейм.

### 2. Налаштування оточення
Створіть файл .env у кореневій директорії проєкту з такими змінними:
```python
DATABASE_URL=postgres://lunch_user:lunch_pass@db:5432/lunch_db
DEBUG=True
SECRET_KEY=your-secret-key-here
```

- `DATABASE_URL`: URL для підключення до PostgreSQL.
- `DEBUG`: True для розробки, False для продакшену.
- `SECRET_KEY`: Унікальний ключ для Django. Згенеруйте його:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```
### 3. Конфігурація Docker
Переконайтеся, що у вас є docker-compose.yml. Ось приклад:
```python
version: '3.8'

services:
  app:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://lunch_user:lunch_pass@db:5432/lunch_db
      - DEBUG=True
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=lunch_user
      - POSTGRES_PASSWORD=lunch_pass
      - POSTGRES_DB=lunch_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 4. Запуск системи
Побудуйте і запустіть контейнери:
```bash
docker-compose up --build
```

- Якщо міграції не застосовуються автоматично, виконайте:
```bash
docker-compose exec app python manage.py migrate
```

API буде доступне на `http://localhost:8000`

### 5. Перевірка роботи
- Використайте curl або браузер:
```bash
curl http://localhost:8000/api/menus/
```
- Очікувана відповідь: `[]` (поки немає меню)

### 6. Запуск тестів
Перевірте функціональність:
```bash
docker-compose exec app pytest -s
```

### 7. Зупинка системи
Зупиніть контейнери:
```bash
docker-compose down
```

Для видалення даних бази:
```bash
docker-compose down -v
```

## Структура проєкту
- `api/`: Моделі, серіалізатори, views для API.
- `tests/`: Тести для версіонування та інших функцій.
- `lunch_service/`: Налаштування Django.
- `Dockerfile`: Опис Docker-образу.
- `docker-compose.yml`: Конфігурація сервісів.
- `requirements.txt`: Залежності проєкту.

## API Ендпоінти
### Авторизація

- `POST /api/token/`: Отримання JWT-токена.
```json
{
  "username": "owner1",
  "password": "password123"
}
```

### Меню
- `POST /api/menus/`: Створення меню. 

Заголовки: 

`Authorization: Bearer <token>`

`X-Build-Version: 1.0` або `2.0`

Тіло для v1.0:
```json
{
  "restaurant_id": 1,
  "items": "{\"main\": \"Pizza Margherita\"}"
}
```

Тіло для v2.0:
```json
{
  "restaurant_id": 1,
  "content": "{\"main\": \"Pizza Margherita\"}"
}
```

Відповідь (v1.0):
```json
{
  "id": 1,
  "restaurant": {"id": 1, "name": "Restaurant 1"},
  "items": {"main": "Pizza Margherita"},
  "date": "2025-03-10"
}
```

Відповідь (v2.0):
```json
{
  "id": 1,
  "restaurant": {"id": 1, "name": "Restaurant 1"},
  "content": {"main": "Pizza Margherita"},
  "date": "2025-03-10"
}
```

`GET /api/menus/`: Список меню 

### Примітки
- Користувач має бути в групі RestaurantOwner для створення меню.
- Повторне створення меню для одного ресторану в той же день повертає `400` з `You can only add one menu per day.`.

### Розробка
- Оновіть `requirements.txt` і перебудуйте:
```bash
docker-compose build
```

- Доступ до shell:
```bash
docker-compose exec app bash
```

- Створення суперкористувача:
```bash
docker-compose exec app python manage.py createsuperuser
```

- Ініціалізація групи RestaurantOwner (якщо не створена):
```python
docker-compose exec app python manage.py shell
```

У shell:
```python
from django.contrib.auth.models import Group
Group.objects.get_or_create(name='RestaurantOwner')
exit()
```

- Перевірка стилю коду з `flake8`:
```bash
docker-compose exec app flake8 .
```
