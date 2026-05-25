.PHONY: up down logs build migrate seed fmt lint test backend-shell bot-shell psql

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=200

build:
	docker compose build

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	docker compose run --rm backend python -m app.seed.run

fmt:
	docker compose run --rm backend ruff format app tests
	cd frontend && npm run format || true

lint:
	docker compose run --rm backend ruff check app tests
	cd frontend && npm run lint || true

test:
	docker compose run --rm backend pytest -q

backend-shell:
	docker compose exec backend bash

bot-shell:
	docker compose exec referee_bot bash

psql:
	docker compose exec postgres psql -U $${POSTGRES_USER:-doings} $${POSTGRES_DB:-doings}
