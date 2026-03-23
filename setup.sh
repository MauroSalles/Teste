#!/usr/bin/env bash
# ============================================================
# setup.sh — Configuração automática do ambiente de desenvolvimento
# Sistema de Gelateria — macOS / Linux
# ============================================================
# Uso: chmod +x setup.sh && ./setup.sh

set -e

# ── Cores ────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # Sem cor

ok()   { echo -e "${GREEN}✅  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️   $1${NC}"; }
err()  { echo -e "${RED}❌  $1${NC}"; }
info() { echo -e "${CYAN}ℹ️   $1${NC}"; }

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   🍦  Setup — Sistema de Gelateria         ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# ── 1. Verificar Git ─────────────────────────────────────────
info "Verificando Git..."
if command -v git &>/dev/null; then
    ok "Git encontrado: $(git --version)"
else
    err "Git não encontrado. Instale em: https://git-scm.com/downloads"
    exit 1
fi

# ── 2. Verificar Python 3.9+ ────────────────────────────────
info "Verificando Python..."
PYTHON_CMD=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VERSION=$("$cmd" -c "import sys; print(sys.version_info[:2])" 2>/dev/null)
        MAJOR=$("$cmd" -c "import sys; print(sys.version_info[0])")
        MINOR=$("$cmd" -c "import sys; print(sys.version_info[1])")
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
            PYTHON_CMD="$cmd"
            ok "Python encontrado: $("$cmd" --version)"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    err "Python 3.9+ não encontrado. Instale em: https://www.python.org/downloads/"
    exit 1
fi

# ── 3. Verificar Node.js 16+ ─────────────────────────────────
info "Verificando Node.js..."
if command -v node &>/dev/null; then
    NODE_MAJOR=$(node -e "console.log(parseInt(process.versions.node))")
    if [ "$NODE_MAJOR" -ge 16 ]; then
        ok "Node.js encontrado: $(node --version)"
    else
        warn "Node.js $(node --version) é mais antigo que 16. Recomendamos atualizar: https://nodejs.org"
    fi
else
    warn "Node.js não encontrado. Instale em: https://nodejs.org (necessário apenas para o frontend)"
fi

# ── 4. Criar ambiente virtual Python ─────────────────────────
info "Criando ambiente virtual Python (venv)..."
if [ -d "venv" ]; then
    warn "Pasta 'venv' já existe — pulando criação."
else
    "$PYTHON_CMD" -m venv venv
    ok "Ambiente virtual criado em ./venv"
fi

# Ativar venv
source venv/bin/activate
ok "Ambiente virtual ativado."

# ── 5. Instalar dependências Python ──────────────────────────
if [ -f "requirements.txt" ]; then
    info "Instalando dependências Python (requirements.txt)..."
    pip install --upgrade pip -q
    pip install -r requirements.txt
    ok "Dependências Python instaladas."
else
    warn "requirements.txt não encontrado — pulando instalação de dependências Python."
fi

# ── 6. Instalar dependências Node.js ─────────────────────────
if [ -f "package.json" ]; then
    info "Instalando dependências Node.js (package.json na raiz)..."
    npm install
    ok "Dependências Node.js instaladas."
fi

for dir in frontend client app; do
    if [ -f "$dir/package.json" ]; then
        info "Instalando dependências Node.js em ./$dir ..."
        (cd "$dir" && npm install)
        ok "Dependências Node.js instaladas em ./$dir"
    fi
done

# ── 7. Criar arquivo .env ─────────────────────────────────────
if [ -f ".env.example" ]; then
    if [ -f ".env" ]; then
        warn "Arquivo .env já existe — não será sobrescrito."
    else
        cp .env.example .env
        ok "Arquivo .env criado a partir do .env.example"
        warn "⚠️  Edite o .env com suas credenciais reais antes de rodar o projeto!"
    fi
else
    warn ".env.example não encontrado — crie o .env manualmente."
fi

# ── 8. Verificar / iniciar PostgreSQL ────────────────────────
info "Verificando PostgreSQL..."
if command -v pg_isready &>/dev/null; then
    if pg_isready -q 2>/dev/null; then
        ok "PostgreSQL está rodando."
    else
        warn "PostgreSQL não está rodando. Tentando iniciar..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &>/dev/null; then
                brew services start postgresql 2>/dev/null || brew services start postgresql@14 2>/dev/null || true
            fi
        else
            sudo systemctl start postgresql 2>/dev/null || sudo service postgresql start 2>/dev/null || true
        fi

        sleep 2
        if pg_isready -q 2>/dev/null; then
            ok "PostgreSQL iniciado com sucesso."
        else
            warn "Não foi possível iniciar o PostgreSQL automaticamente."
            warn "Inicie manualmente e execute: alembic upgrade head"
        fi
    fi
else
    warn "PostgreSQL não encontrado. Instale em: https://www.postgresql.org/download/"
fi

# ── 9. Executar migrations ───────────────────────────────────
if [ -f "alembic.ini" ] && pg_isready -q 2>/dev/null; then
    info "Executando migrations do banco de dados..."
    alembic upgrade head && ok "Migrations executadas com sucesso." || warn "Falha nas migrations — verifique as configurações do banco no .env"
elif [ -f "backend/app.py" ] && pg_isready -q 2>/dev/null; then
    info "Criando tabelas via Flask (db.create_all)..."
    "$PYTHON_CMD" -c "
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))
try:
    from app import app, db
    with app.app_context():
        db.create_all()
    print('Tabelas criadas com sucesso.')
except Exception as e:
    print(f'Aviso: {e}')
" 2>/dev/null || true
fi

# ── 10. Resumo final ──────────────────────────────────────────
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   ✅  Setup concluído!                     ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${CYAN}📋 Próximos passos:${NC}"
echo ""
echo "  1. Edite o arquivo .env com suas credenciais:"
echo "     nano .env    (ou abra no VS Code)"
echo ""
echo "  2. Inicie o backend:"
echo "     source venv/bin/activate"
echo "     python backend/app.py"
echo "     → Acesse: http://localhost:5000"
echo ""
echo "  3. Inicie o frontend (em outro terminal):"
echo "     cd frontend && npm start"
echo "     → Acesse: http://localhost:3000"
echo ""
echo "  4. Ou use o script auxiliar para iniciar tudo:"
echo "     ./start-dev.sh"
echo ""
echo -e "${CYAN}📚 Documentação:${NC}"
echo "  SETUP_LOCAL.md        — Guia completo"
echo "  REQUISITOS.md         — O que precisa instalar"
echo "  TROUBLESHOOTING_VERCEL.md — Problemas com Vercel"
echo ""
