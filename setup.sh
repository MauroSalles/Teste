#!/usr/bin/env bash
# ============================================================
# Gelateria Sistema — Setup Automático Local
# Uso: ./setup.sh
# ============================================================
set -euo pipefail

GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
ok()   { echo -e "${GREEN}✓ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠ $*${NC}"; }
err()  { echo -e "${RED}✗ $*${NC}"; exit 1; }
step() { echo -e "\n${YELLOW}▶ $*${NC}"; }

echo -e "${GREEN}"
echo "  🍦 Gelateria Sistema — Setup Local"
echo "  ====================================${NC}"

# ── 1. Python 3.9+ ──────────────────────────────────────────
step "Verificando Python..."
if ! command -v python3 &>/dev/null; then
  err "Python 3 não encontrado. Instale em https://python.org"
fi
PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ok "Python $PY_VER detectado"
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)"; then
  ok "Versão compatível"
else
  err "Python 3.9+ requerido. Versão atual: $PY_VER"
fi

# ── 2. Virtual environment ───────────────────────────────────
step "Criando ambiente virtual..."
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ok "Ambiente virtual criado em .venv"
else
  ok "Ambiente virtual já existe"
fi
# shellcheck source=/dev/null
source .venv/bin/activate
ok "Ambiente virtual ativado"

# ── 3. Dependências Python ───────────────────────────────────
step "Instalando dependências Python..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt pytest pytest-cov
ok "Dependências instaladas"

# ── 4. Arquivo .env ─────────────────────────────────────────
step "Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
  cp .env.example .env
  warn ".env criado a partir de .env.example — edite as credenciais do banco"
else
  ok ".env já existe"
fi

# ── 5. PostgreSQL ────────────────────────────────────────────
step "Verificando PostgreSQL..."
if command -v psql &>/dev/null; then
  ok "psql encontrado: $(psql --version | head -1)"
  warn "Certifique-se de ter um banco 'gelateria' criado:"
  echo "    createdb gelateria"
  echo "    psql -d gelateria -f database/schema.sql"
else
  warn "psql não encontrado no PATH. Opções:"
  echo "  • Instalar PostgreSQL: https://postgresql.org/download"
  echo "  • Ou rodar via Docker: docker-compose up -d"
fi

# ── 6. Resumo ────────────────────────────────────────────────
echo ""
echo -e "${GREEN}  ✅ Setup concluído!${NC}"
echo ""
echo "  Próximos passos:"
echo "    1. Edite .env com suas credenciais"
echo "    2. Crie o banco: createdb gelateria && psql -d gelateria -f database/schema.sql"
echo "    3. Inicie o backend:  source .venv/bin/activate && python -m flask run"
echo "    4. Abra o frontend:   abra frontend/index.html no navegador"
echo "    5. Rode os testes:    pytest tests/ -v"
echo ""
