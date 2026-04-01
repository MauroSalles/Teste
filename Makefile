.PHONY: install dev test lint docker-up docker-down db-migrate clean

install:
	pip install -r requirements.txt

dev:
	FLASK_ENV=development flask --app backend.app run --debug --port 5000

test:
	PYTHONPATH=$(PWD) pytest tests/ -v --tb=short

lint:
	flake8 backend --count --select=E9,F63,F7,F82 --show-source --statistics

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down

db-migrate:
	psql $${DATABASE_URL} -f database/schema.sql

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -f .coverage
	rm -rf .pytest_cache htmlcov
