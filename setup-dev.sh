#!/usr/bin/env bash
# =============================================================================
# setup-dev.sh — Setup do Ambiente de Desenvolvimento Local
# =============================================================================
# Uso: bash setup-dev.sh
#
# Este script instala todas as dependências e configura o ambiente local
# para rodar o projeto Gelateria CMD-Web com Docker.
# =============================================================================

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # Sem cor

print_step()  { echo -e "\n${CYAN}▶ $1${NC}"; }
print_ok()    { echo -e "${GREEN}✅ $1${NC}"; }
print_warn()  { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info()  { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║     🍦 GELATERIA CMD-WEB — SETUP LOCAL           ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# -----------------------------------------------------------------------------
# 1. Verificar pré-requisitos
# -----------------------------------------------------------------------------
print_step "Verificando pré-requisitos..."

check_command() {
    if command -v "$1" &>/dev/null; then
        print_ok "$1 encontrado: $(command -v "$1")"
    else
        print_error "$1 não encontrado. Instale em: $2"
        exit 1
    fi
}

check_command "git"    "https://git-scm.com"
check_command "docker" "https://docs.docker.com/get-docker/"

# Verificar docker compose (v2) ou docker-compose (v1)
if docker compose version &>/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
    print_ok "Docker Compose v2 encontrado"
elif command -v docker-compose &>/dev/null; then
    DOCKER_COMPOSE="docker-compose"
    print_ok "Docker Compose v1 encontrado"
else
    print_error "Docker Compose não encontrado. Instale em: https://docs.docker.com/compose/install/"
    exit 1
fi

# -----------------------------------------------------------------------------
# 2. Criar arquivo .env se não existir
# -----------------------------------------------------------------------------
print_step "Configurando variáveis de ambiente..."

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_ok ".env criado a partir de .env.example"
        print_warn "Edite o arquivo .env com suas configurações antes de continuar"
        print_info "Abrindo .env para edição em 3 segundos... (Ctrl+C para cancelar)"
        sleep 3
        "${EDITOR:-nano}" .env || true
    else
        print_warn ".env.example não encontrado. Criando .env básico..."
        cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gelateria
DB_USER=gelateria_user
DB_PASSWORD=gelateria_dev_password_123
DATABASE_URL=postgresql://gelateria_user:gelateria_dev_password_123@localhost:5432/gelateria
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev_secret_key_nao_usar_em_producao
PORT=5000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
VITE_API_URL=http://localhost:5000
EOF
        print_ok ".env básico criado"
    fi
else
    print_ok ".env já existe"
fi

# -----------------------------------------------------------------------------
# 3. Verificar se Docker está rodando
# -----------------------------------------------------------------------------
print_step "Verificando se Docker está em execução..."

if ! docker info &>/dev/null 2>&1; then
    print_error "Docker não está em execução. Inicie o Docker e tente novamente."
    exit 1
fi
print_ok "Docker está rodando"

# -----------------------------------------------------------------------------
# 4. Construir e iniciar containers
# -----------------------------------------------------------------------------
print_step "Construindo imagens Docker..."
$DOCKER_COMPOSE build --no-cache

print_step "Iniciando containers em background..."
$DOCKER_COMPOSE up -d

# -----------------------------------------------------------------------------
# 5. Aguardar banco de dados
# -----------------------------------------------------------------------------
print_step "Aguardando banco de dados PostgreSQL ficar pronto..."

MAX_TRIES=30
COUNT=0
until $DOCKER_COMPOSE exec -T db pg_isready -U gelateria_user -d gelateria &>/dev/null 2>&1; do
    COUNT=$((COUNT + 1))
    if [ "$COUNT" -ge "$MAX_TRIES" ]; then
        print_error "Timeout aguardando PostgreSQL. Verifique os logs: $DOCKER_COMPOSE logs db"
        exit 1
    fi
    echo -n "."
    sleep 2
done
echo ""
print_ok "PostgreSQL está pronto!"

# -----------------------------------------------------------------------------
# 6. Rodar migrações/seed do banco
# -----------------------------------------------------------------------------
print_step "Executando migrações do banco de dados..."
$DOCKER_COMPOSE exec -T backend python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Tabelas criadas com sucesso!')
" 2>/dev/null || print_warn "Migração automática não disponível. Verifique a documentação."

# -----------------------------------------------------------------------------
# 7. Verificar se serviços estão respondendo
# -----------------------------------------------------------------------------
print_step "Verificando serviços..."

sleep 3

if curl -sf http://localhost:5000/health &>/dev/null; then
    print_ok "Backend rodando em http://localhost:5000"
else
    print_warn "Backend ainda não respondendo. Aguarde alguns segundos e tente: curl http://localhost:5000/health"
fi

if curl -sf http://localhost:3000 &>/dev/null; then
    print_ok "Frontend rodando em http://localhost:3000"
else
    print_warn "Frontend ainda não respondendo. Aguarde alguns segundos."
fi

# -----------------------------------------------------------------------------
# Resumo final
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║          ✅ SETUP CONCLUÍDO COM SUCESSO!         ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📋 Serviços disponíveis:${NC}"
echo -e "  🌐 Frontend:  ${BLUE}http://localhost:3000${NC}"
echo -e "  🔧 Backend:   ${BLUE}http://localhost:5000${NC}"
echo -e "  🗄️  Database:  ${BLUE}localhost:5432${NC} (gelateria)"
echo ""
echo -e "${CYAN}📋 Comandos úteis:${NC}"
echo -e "  ${YELLOW}$DOCKER_COMPOSE logs -f${NC}          → Ver logs em tempo real"
echo -e "  ${YELLOW}$DOCKER_COMPOSE ps${NC}               → Listar containers"
echo -e "  ${YELLOW}$DOCKER_COMPOSE down${NC}             → Parar tudo"
echo -e "  ${YELLOW}$DOCKER_COMPOSE restart backend${NC}  → Reiniciar backend"
echo ""
print_info "Para parar o ambiente: $DOCKER_COMPOSE down"
print_info "Para parar e apagar dados: $DOCKER_COMPOSE down -v"
