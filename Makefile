# Makefile — Gelateria Pro development helpers
# Usage: make <target>

.PHONY: install dev test lint docker-up docker-down db-migrate clean

install:
	pip install -r requirements.txt

dev:
	FLASK_ENV=development PYTHONPATH=. flask --app backend.app run --debug --port 5000

test:
	PYTHONPATH=. pytest tests/ -v --cov=backend

lint:
	flake8 backend/

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

db-migrate:
	psql $(DATABASE_URL) -f database/schema.sql

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -f .coverage
