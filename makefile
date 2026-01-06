# Makefile
.PHONY: help build up down logs clean migrate test stop start restart

help:
	@echo "Доступные команды:"
	@echo "  make build     - Собрать контейнеры"
	@echo "  make up        - Запустить контейнеры в фоне"
	@echo "  make start     - Запустить существующие контейнеры"
	@echo "  make stop      - Остановить контейнеры"
	@echo "  make restart   - Перезапустить контейнеры"
	@echo "  make down      - Остановить и удалить контейнеры"
	@echo "  make logs      - Показать логи"
	@echo "  make clean     - Очистить всё"
	@echo "  make migrate   - Выполнить миграции"
	@echo "  make test      - Запустить тесты"
	@echo ""
	@echo "Доступ к сервисам:"
	@echo "  Frontend:      http://localhost:8080"
	@echo "  Backend API:   http://localhost:8001"
	@echo "  PostgreSQL:    localhost:5433"
	@echo ""

build:
	docker-compose build --no-cache

up:
	docker-compose up -d

start:
	docker-compose start

stop:
	docker-compose stop

restart:
	docker-compose restart

down:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f --volumes

migrate:
	docker-compose exec backend alembic upgrade head

migrate-create:
	docker-compose exec backend alembic revision --autogenerate -m "$(message)"

test:
	docker-compose exec backend pytest

shell:
	docker-compose exec backend bash

db-shell:
	docker-compose exec postgres psql -U filecloud_user -d filecloud

status:
	docker-compose ps

volumes:
	docker volume ls
