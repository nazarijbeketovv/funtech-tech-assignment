INFRA_PATH = .local_dev/docker-compose.infra.local.yml
COMPOSE_PATH = docker-compose.yml
DC = docker compose


.PHONY: type lint env infra migrations migrate app

type:
	mypy .

lint:
	ruff format .
	ruff check . --fix

env:
	cp env.template .env


infra:
	$(DC) -f $(INFRA_PATH) up --build -d


migrations:
	PYTHONPATH=src alembic revision --autogenerate -m "$(msg)"

migrate:
	PYTHONPATH=src alembic upgrade head

app:
	$(DC) -f $(COMPOSE_PATH) up --build