# Guidebook REST API

REST API приложение для справочника организаций, зданий и видов деятельности.

## Описание

Приложение предоставляет API для работы со справочником, который содержит:
- **Организации** - карточки организаций с названием, телефонами, зданием и видами деятельности
- **Здания** - информация о зданиях с адресами и географическими координатами
- **Деятельности** - иерархическая классификация видов деятельности (до 3 уровней вложенности)

## Технологии

- **FastAPI** - веб-фреймворк
- **SQLAlchemy** - ORM
- **Alembic** - миграции базы данных
- **PostgreSQL** - база данных
- **Pydantic** - валидация данных
- **GeoAlchemy2** - работа с геоданными
- **Docker** - контейнеризация

## Быстрый старт

### С использованием Docker Compose

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd guidebook_rest_api
```

2. Запустите приложение:
```bash
docker-compose up --build
```

3. Приложение будет доступно по адресу: http://localhost:8000
4. Документация API: http://localhost:8000/docs

### Локальная установка(ручная)

1. Установите PostgreSQL и создайте базу данных
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Настройте переменные окружения:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
export API_KEY="your-secret-api-key"
```

4. Примените миграции:
```bash
alembic upgrade head
```

5. Заполните тестовыми данными:
```bash
python -m app.seed_data
```

6. Запустите приложение:
```bash
uvicorn app.main:app --reload
```

## API Endpoints
При пересборке проекта ID организаций меняются !

### Аутентификация
Все запросы требуют API ключ в заголовке `X-API-Key`.

### Организации

- `GET /api/organizations/` - список всех организаций
- `GET /api/organizations/{id}` - информация об организации по ID
        curl -X GET "http://localhost:8000/api/organizations/8db13a31-f57a-4bfa-b83a-1a07236673e6" \
        -H "X-API-Key: your-secret-api-key-here"
- `GET /api/organizations/search/` - поиск организаций по названию
        curl -X GET "http://localhost:8000/api/organizations/search/?name=%D0%A0%D0%BE%D0%B3%D0%B0" -H "X-API-Key: your-secret-api-key-here"
- `GET /api/organizations/by-building/{building_id}` - организации в здании
        curl -X GET "http://localhost:8000/api/organizations/by-building/4df7df3e-5f71-41c5-9b20-122c3b48400e" \
        -H "X-API-Key: your-secret-api-key-here" \
        -H "accept: application/json"
- `GET /api/organizations/by-activity/{activity_id}` - организации по виду деятельности
        curl -X GET "http://localhost:8000/api/organizations/by-activity/9f097b53-67d8-42bf-b959-f127294a66c8" \
        -H "X-API-Key: your-secret-api-key-here" \
        -H "accept: application/json"
- `GET /api/organizations/nearby/` - организации в радиусе/области
        # Поиск в радиусе 5 км от точки (55.7558, 37.6176)
        curl -X GET "http://localhost:8000/api/organizations/nearby/?latitude=55.7558&longitude=37.6176&radius_km=5" \
        -H "X-API-Key: your-secret-api-key-here" \
        -H "accept: application/json"

        # Поиск в прямоугольной области
        curl -X GET "http://localhost:8000/api/organizations/nearby/?latitude=55.7558&longitude=37.6176&min_lat=55.7500&max_lat=55.7600&min_lon=37.6100&max_lon=37.6200" \
        -H "X-API-Key: your-secret-api-key-here" \
        -H "accept: application/json"


Поиск организаций по виду деятельности (включая дерево)
- `GET /api/organizations/by-activity-tree/{activity_id}`
        curl -X GET "http://localhost:8000/api/organizations/by-activity-tree/eb3b2cb2-910b-4130-9787-43e0510745ce" -H "X-API-Key: your-secret-api-key-here"
        Результат: Находит организации с видами деятельности "Еда", "Мясная продукция", "Молочная продукция", "Хлебобулочные изделия"


### Здания

- `GET /api/buildings/` - список всех зданий
- `GET /api/buildings/{id}` - информация о здании по ID

### Деятельности

- `GET /api/activities/` - список всех видов деятельности
- `GET /api/activities/{id}` - информация о виде деятельности по ID
- `GET /api/activities/tree/` - дерево видов деятельности

## Структура базы данных

### Таблицы:
- `organizations` - организации
- `buildings` - здания
- `activities` - виды деятельности
- `organization_phones` - телефоны организаций
- `organization_activities` - связь организаций с видами деятельности

### Ключевые особенности:
- Географические координаты зданий (PostGIS)
- Иерархическая структура видов деятельности
- Ограничение вложенности деятельности до 3 уровней
- Связи многие-ко-многим для телефонов и видов деятельности

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных
- `API_KEY` - секретный ключ для аутентификации API

## Разработка

### Создание миграции:
```bash
alembic revision --autogenerate -m "Description"
```

### Применение миграций:
```bash
alembic upgrade head
```

### Откат миграции:
```bash
alembic downgrade -1
```

## Тестирование

Swagger UI: http://localhost:8000/docs
