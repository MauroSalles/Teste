#!/usr/bin/env bash
# ============================================================
# start-postgres.sh — Inicia o PostgreSQL localmente
# Sistema de Gelateria — macOS / Linux
# ============================================================
# Uso: chmod +x start-postgres.sh && ./start-postgres.sh

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅  $1${NC}"; }
info() { echo -e "${CYAN}ℹ️   $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $1${NC}"; }
err()  { echo -e "${RED}❌  $1${NC}"; }

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   🗄️  Iniciando PostgreSQL                 ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Verificar se PostgreSQL está disponível
if ! command -v pg_isready &>/dev/null && ! command -v psql &>/dev/null; then
    err "PostgreSQL não encontrado."
    echo ""
    echo "Instale o PostgreSQL:"
    echo "  macOS:  brew install postgresql"
    echo "  Ubuntu: sudo apt install postgresql"
    echo "  Link:   https://www.postgresql.org/download/"
    exit 1
fi

# Verificar se já está rodando
if pg_isready -q 2>/dev/null; then
    ok "PostgreSQL já está rodando na porta 5432."
else
    info "PostgreSQL não está rodando. Tentando iniciar..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &>/dev/null; then
            for pg_version in postgresql postgresql@15 postgresql@14 postgresql@13 postgresql@12; do
                if brew services list | grep -q "$pg_version"; then
                    brew services start "$pg_version" 2>/dev/null && break
                fi
            done
        else
            warn "Homebrew não encontrado. Inicie o PostgreSQL manualmente."
        fi
    else
        # Linux
        sudo systemctl start postgresql 2>/dev/null \
            || sudo service postgresql start 2>/dev/null \
            || warn "Não foi possível iniciar o PostgreSQL automaticamente."
    fi

    sleep 2

    if pg_isready -q 2>/dev/null; then
        ok "PostgreSQL iniciado com sucesso na porta 5432."
    else
        err "Não foi possível iniciar o PostgreSQL."
        echo ""
        echo "Tente manualmente:"
        echo "  macOS:  brew services start postgresql"
        echo "  Linux:  sudo systemctl start postgresql"
        exit 1
    fi
fi

# Carregar variáveis do .env de forma segura
if [ -f ".env" ]; then
    set -a
    # shellcheck source=.env
    source .env
    set +a
fi

DB_NAME="${DB_NAME:-gelateria}"
DB_USER="${DB_USER:-postgres}"

# Verificar se o banco de dados existe
info "Verificando banco de dados '$DB_NAME'..."

DB_EXISTS=$(psql -U "$DB_USER" -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>/dev/null || echo "0")

if [ "$DB_EXISTS" = "1" ]; then
    ok "Banco de dados '$DB_NAME' já existe."
else
    info "Criando banco de dados '$DB_NAME'..."
    createdb -U "$DB_USER" "$DB_NAME" 2>/dev/null \
        && ok "Banco de dados '$DB_NAME' criado." \
        || warn "Não foi possível criar o banco automaticamente. Crie manualmente: createdb $DB_NAME"
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   PostgreSQL pronto!                       ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "  Host:     localhost"
echo "  Porta:    5432"
echo "  Banco:    $DB_NAME"
echo "  Usuário:  $DB_USER"
echo ""
echo "  Conectar via psql:"
echo "  psql -U $DB_USER -d $DB_NAME"
echo ""
echo "  Ou abra o pgAdmin: https://www.pgadmin.org"
echo ""
