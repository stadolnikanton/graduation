# FileCloud 🚀

Облачное хранилище файлов с временными ссылками для обмена.

## 🛠️ Стек

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Storage:** MinIO (S3-совместимое)
- **Cache:** Redis
- **Auth:** JWT (access + refresh)

## 🚀 Быстрый старт

### 1. Клонирование
```bash
git clone https://github.com/stadolnikanton/graduation.git
cd graduation
```

### 2. Настройка (опционально)
```bash
cp .env.example .env
# Все параметры имеют значения по умолчанию
```

### 3. Запуск
```bash
docker-compose up -d --build
```

Миграции применяются автоматически.

## 📍 Сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| **API** | http://localhost:8000 | REST API |
| **Docs** | http://localhost:8000/docs | Swagger UI |
| **MinIO** | http://localhost:9001 | Консоль (minioadmin/minioadmin) |
| **PostgreSQL** | localhost:5432 | База данных |
| **Redis** | localhost:6379 | Кэш |

## 📚 API Endpoints

### Auth
- `POST /v1/auth/register` — Регистрация
- `POST /v1/auth/login` — Вход
- `POST /v1/auth/logout` — Выход
- `POST /v1/auth/refresh` — Обновление токена
- `GET /v1/auth/me` — Текущий пользователь

### Files
- `GET /v1/files` — Список файлов
- `POST /v1/files/upload` — Загрузка файла
- `GET /v1/files/{id}` — Скачать файл
- `DELETE /v1/files/{id}` — Удалить файл

### Share
- `POST /v1/share/{file_id}` — Создать ссылку
- `GET /v1/share/{token}` — Скачать по ссылке
- `GET /v1/share/{token}/info` — Информация о ссылке
- `DELETE /v1/share/{token}` — Удалить ссылку

## 🔧 Команды

```bash
# Просмотр логов
docker-compose logs -f backend

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
```

## 📝 Лицензия

Учебный проект.

---

**Версия:** 1.0.1
