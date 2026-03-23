#!/usr/bin/env bash
# ============================================================
# start-dev.sh — Inicia backend e frontend em paralelo
# Sistema de Gelateria — macOS / Linux
# ============================================================
# Uso: chmod +x start-dev.sh && ./start-dev.sh

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅  $1${NC}"; }
info() { echo -e "${CYAN}ℹ️   $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $1${NC}"; }

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   🍦  Iniciando ambiente de desenvolvimento ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Verificar se o venv existe
if [ ! -d "venv" ]; then
    warn "Ambiente virtual não encontrado. Execute ./setup.sh primeiro."
    exit 1
fi

# Verificar se o .env existe
if [ ! -f ".env" ]; then
    warn ".env não encontrado. Copiando .env.example..."
    cp .env.example .env 2>/dev/null || true
    warn "Edite o .env com suas credenciais antes de continuar."
fi

# Ativar venv
source venv/bin/activate
ok "Ambiente virtual ativado."

# Limpar processos anteriores
info "Verificando portas 5000 e 3000..."
if command -v fuser &>/dev/null; then
    fuser -k 5000/tcp 2>/dev/null || true
    fuser -k 3000/tcp 2>/dev/null || true
else
    # macOS fallback
    lsof -ti:5000 2>/dev/null | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 2>/dev/null | xargs kill -9 2>/dev/null || true
fi

# Iniciar backend
info "Iniciando backend Flask na porta 5000..."
if [ -f "backend/app.py" ]; then
    python backend/app.py &
    BACKEND_PID=$!
    sleep 2
    ok "Backend rodando em http://localhost:5000 (PID: $BACKEND_PID)"
else
    warn "backend/app.py não encontrado."
fi

# Iniciar frontend
FRONTEND_DIR=""
for dir in frontend client app; do
    if [ -f "$dir/package.json" ]; then
        FRONTEND_DIR="$dir"
        break
    fi
done

if [ -n "$FRONTEND_DIR" ]; then
    info "Iniciando frontend em ./$FRONTEND_DIR (porta 3000)..."
    (cd "$FRONTEND_DIR" && npm start) &
    FRONTEND_PID=$!
    sleep 3
    ok "Frontend rodando em http://localhost:3000 (PID: $FRONTEND_PID)"
else
    warn "Frontend não encontrado (nenhuma pasta com package.json)."
fi

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Ambiente de desenvolvimento iniciado!    ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  🔧 Backend:  ${CYAN}http://localhost:5000${NC}"
echo -e "  🎨 Frontend: ${CYAN}http://localhost:3000${NC}"
echo ""
echo "  Pressione Ctrl+C para parar todos os servidores."
echo ""

# Aguardar interrupção
trap "echo ''; warn 'Encerrando servidores...'; [ -n \"$BACKEND_PID\" ] && kill \"$BACKEND_PID\" 2>/dev/null; [ -n \"$FRONTEND_PID\" ] && kill \"$FRONTEND_PID\" 2>/dev/null; ok 'Servidores encerrados.'" SIGINT SIGTERM

wait
