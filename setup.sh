#!/usr/bin/env bash
# setup.sh — Configura o ambiente de desenvolvimento local automaticamente.
# Uso: ./setup.sh

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${GREEN}[+]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }

echo ""
echo "🍦  Gelateria Sistema — Setup Local"
echo "════════════════════════════════════"
echo ""

# ── 1. Check Python ──────────────────────────────────────────────────────────
info "Verificando Python..."
if ! command -v python3 &>/dev/null; then
    error "Python 3 não encontrado. Consulte REQUISITOS.md para instalar."
fi
PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PY_VERSION encontrado."

# ── 2. Virtual environment ───────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    info "Criando ambiente virtual Python em .venv..."
    python3 -m venv .venv
else
    info "Ambiente virtual .venv já existe."
fi

info "Ativando ambiente virtual..."
# shellcheck source=/dev/null
source .venv/bin/activate

# ── 3. Install dependencies ──────────────────────────────────────────────────
info "Instalando dependências Python..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
info "Dependências instaladas."

# ── 4. .env file ─────────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
    info "Criando .env a partir do .env.example..."
    cp .env.example .env
    warn "⚠  Edite o arquivo .env com suas credenciais do banco antes de continuar."
    warn "   nano .env   ou   code .env"
else
    info ".env já existe — mantendo configurações existentes."
fi

# ── 5. Check PostgreSQL ──────────────────────────────────────────────────────
info "Verificando PostgreSQL..."
if ! command -v psql &>/dev/null; then
    warn "psql não encontrado. Pulando inicialização do banco."
    warn "Consulte REQUISITOS.md para instalar o PostgreSQL."
else
    # Load .env variables
    set -a
    # shellcheck source=.env
    source .env 2>/dev/null || true
    set +a

    DB_HOST_FINAL="${DB_HOST:-localhost}"
    DB_PORT_FINAL="${DB_PORT:-5432}"
    DB_NAME_FINAL="${DB_NAME:-gelateria}"
    DB_USER_FINAL="${DB_USER:-postgres}"

    if pg_isready -h "$DB_HOST_FINAL" -p "$DB_PORT_FINAL" -q; then
        info "PostgreSQL disponível em $DB_HOST_FINAL:$DB_PORT_FINAL."

        # Create database if needed
        if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST_FINAL" -p "$DB_PORT_FINAL" \
               -U "$DB_USER_FINAL" -lqt 2>/dev/null | cut -d'|' -f1 | grep -qw "$DB_NAME_FINAL"; then
            info "Criando banco de dados '$DB_NAME_FINAL'..."
            PGPASSWORD="$DB_PASSWORD" createdb -h "$DB_HOST_FINAL" -p "$DB_PORT_FINAL" \
                -U "$DB_USER_FINAL" "$DB_NAME_FINAL" 2>/dev/null || true
        else
            info "Banco '$DB_NAME_FINAL' já existe."
        fi

        info "Aplicando schema..."
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST_FINAL" -p "$DB_PORT_FINAL" \
            -U "$DB_USER_FINAL" -d "$DB_NAME_FINAL" -f database/schema.sql -q
        info "Schema aplicado com sucesso."
    else
        warn "PostgreSQL não está rodando em $DB_HOST_FINAL:$DB_PORT_FINAL."
        warn "Inicie o PostgreSQL e execute: psql -h $DB_HOST_FINAL -U $DB_USER_FINAL -d $DB_NAME_FINAL -f database/schema.sql"
    fi
fi

# ── 6. Done ──────────────────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════"
echo -e "${GREEN}✅  Setup concluído!${NC}"
echo ""
echo "Para iniciar o backend:"
echo "  source .venv/bin/activate"
echo "  python -m backend.app"
echo ""
echo "Para abrir o frontend:"
echo "  cd frontend && python3 -m http.server 5500"
echo "  Acesse: http://localhost:5500"
echo ""
echo "Para rodar os testes:"
echo "  pytest tests/ -v"
echo ""
echo "Ou use o Makefile: make help"
echo ""
