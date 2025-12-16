INFRA_PATH = .local_dev/docker-compose.infra.local.yml
DC = docker compose
ALEMBIC = alembic -c alembic.ini
ALEMBIC_ENV = PYTHONPATH=src
ALEMBIC_DB_ENV = $(if $(strip $(DATABASE_URL)),DATABASE_URL="$(DATABASE_URL)",)

MIGRATION ?= init

.PHONY: type lint env infra migration migrate

type:
	mypy .

lint:
	ruff format .
	ruff check . --fix

env:
	cp env.template .env


infra:
	$(DC) -f $(INFRA_PATH) up --build -d

migration:
	$(ALEMBIC_ENV) $(ALEMBIC_DB_ENV) $(ALEMBIC) revision --autogenerate -m "$(MIGRATION)"

migrate:
	$(ALEMBIC_ENV) $(ALEMBIC_DB_ENV) $(ALEMBIC) upgrade head