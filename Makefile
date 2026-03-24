# Gelateria Sistema — Makefile
# Uso: make <comando>

.PHONY: help install setup test test-cov lint run run-frontend docker-up docker-down clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

# ── Ajuda ────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "🍦  Gelateria Sistema — Comandos disponíveis"
	@echo "══════════════════════════════════════════"
	@echo "  make install      Instala dependências Python no virtualenv"
	@echo "  make setup        Setup completo (venv + deps + banco)"
	@echo "  make test         Roda testes com pytest"
	@echo "  make test-cov     Roda testes com relatório de cobertura"
	@echo "  make lint         Verifica estilo do código (flake8)"
	@echo "  make run          Inicia o backend em modo desenvolvimento"
	@echo "  make run-frontend Serve o frontend em localhost:5500"
	@echo "  make docker-up    Sobe todos os serviços com Docker Compose"
	@echo "  make docker-down  Para os serviços Docker"
	@echo "  make clean        Remove arquivos temporários e caches"
	@echo ""

# ── Instalação ───────────────────────────────────────────────────────────────
$(VENV)/bin/activate:
	python3 -m venv $(VENV)

install: $(VENV)/bin/activate
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r requirements.txt --quiet
	@echo "✅ Dependências instaladas."

setup:
	@bash setup.sh

# ── Testes ───────────────────────────────────────────────────────────────────
test: install
	$(PYTEST) tests/ -v --tb=short

test-cov: install
	$(PYTEST) tests/ -v --tb=short --cov=backend --cov-report=term-missing

# ── Linting ──────────────────────────────────────────────────────────────────
lint: install
	@$(VENV)/bin/flake8 backend/ tests/ --max-line-length=120 --ignore=E501 2>/dev/null || \
	  ($(PIP) install flake8 --quiet && $(VENV)/bin/flake8 backend/ tests/ --max-line-length=120)

# ── Executar ─────────────────────────────────────────────────────────────────
run: install
	FLASK_ENV=development $(PYTHON) -m backend.app

run-frontend:
	@echo "Abrindo frontend em http://localhost:5500"
	cd frontend && python3 -m http.server 5500

# ── Docker ───────────────────────────────────────────────────────────────────
docker-up:
	docker-compose up

docker-down:
	docker-compose down

# ── Limpeza ──────────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov/
	@echo "✅ Arquivos temporários removidos."
