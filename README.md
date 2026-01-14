# Graduation Project

Дипломный проект с использованием Docker и Docker Compose для запуска backend, frontend и базы данных PostgreSQL.

## Требования

Перед началом работы убедитесь, что у вас установлены:

- Docker
- Docker Compose
- Make

## Быстрый старт

```bash
make build
make up
```

После запуска сервисы будут доступны по адресам:

- **Frontend:** [http://localhost:8080](http://localhost:8080)
- **Backend API:** [http://localhost:8001](http://localhost:8001)
- **PostgreSQL:** localhost:5433
- **MiniO:** [http://localhost:9000](http://localhost:9000)

## Управление проектом

В проекте используется `Makefile` для упрощения работы с Docker-контейнерами.

### Основные команды

```bash
make help        # Показать все доступные команды
make build       # Собрать контейнеры без кэша
make up          # Запустить контейнеры в фоне
make start       # Запустить существующие контейнеры
make stop        # Остановить контейнеры
make restart     # Перезапустить контейнеры
make down        # Остановить и удалить контейнеры
make logs        # Просмотр логов
make status      # Статус контейнеров
```

### Очистка

```bash
make clean       # Полная очистка (контейнеры, volumes, orphan-сервисы)
```

## Backend

### Миграции базы данных

```bash
make migrate                     # Применить миграции
make migrate-create message="msg" # Создать новую миграцию
```

### Тесты

```bash
make test
```

### Shell-доступ

```bash
make shell      # Bash внутри backend-контейнера
make db-shell   # psql внутри PostgreSQL
```

## Volumes

```bash
make volumes    # Список docker volumes
```

## Структура проекта

Проект разделён на сервисы:

- **Frontend** — пользовательский интерфейс
- **Backend** — API и бизнес-логика
- **PostgreSQL** — база данных

## Репозиторий

GitHub: [https://github.com/stadolnikanton/graduation](https://github.com/stadolnikanton/graduation)

---

Проект выполнен в рамках дипломной работы.
