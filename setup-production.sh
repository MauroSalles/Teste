#!/usr/bin/env bash
# =============================================================================
# setup-production.sh — Configuração de Secrets e Deploy em Produção
# =============================================================================
# Uso: bash setup-production.sh
#
# Este script auxilia na configuração de todos os secrets necessários no
# GitHub para o deploy automático via GitHub Actions.
#
# Pré-requisitos:
#   - GitHub CLI (gh) instalado e autenticado
#   - Conta no Render.com configurada
#   - Conta no Vercel configurada
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

print_step()  { echo -e "\n${CYAN}${BOLD}▶ $1${NC}"; }
print_ok()    { echo -e "${GREEN}✅ $1${NC}"; }
print_warn()  { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info()  { echo -e "${BLUE}ℹ️  $1${NC}"; }
prompt()      { echo -e "${YELLOW}? $1${NC}"; }

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║  🚀 GELATERIA — CONFIGURAÇÃO DE PRODUÇÃO        ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

# -----------------------------------------------------------------------------
# Verificar pré-requisitos
# -----------------------------------------------------------------------------
print_step "Verificando pré-requisitos..."

if ! command -v gh &>/dev/null; then
    print_error "GitHub CLI (gh) não encontrado!"
    echo ""
    echo "Instale em:"
    echo "  Linux:  sudo apt install gh  OU  https://cli.github.com"
    echo "  Mac:    brew install gh"
    echo "  Win:    winget install GitHub.cli"
    exit 1
fi

if ! gh auth status &>/dev/null 2>&1; then
    print_warn "GitHub CLI não está autenticado. Iniciando autenticação..."
    gh auth login
fi

print_ok "GitHub CLI autenticado: $(gh auth status 2>&1 | grep 'Logged in' | head -1)"

# -----------------------------------------------------------------------------
# Identificar repositório
# -----------------------------------------------------------------------------
print_step "Identificando repositório..."

REPO=$(git remote get-url origin | sed 's|https://github.com/||;s|git@github.com:||;s|\.git$||')
echo -e "Repositório detectado: ${BLUE}${REPO}${NC}"
echo ""
prompt "Confirma? (Enter = sim, ou digite o repositório no formato owner/repo):"
read -r REPO_INPUT
if [ -n "$REPO_INPUT" ]; then
    REPO="$REPO_INPUT"
fi
print_ok "Usando repositório: $REPO"

# -----------------------------------------------------------------------------
# Função para definir secret
# -----------------------------------------------------------------------------
set_secret() {
    local SECRET_NAME="$1"
    local SECRET_DESC="$2"
    local SECRET_EXAMPLE="$3"

    echo ""
    echo -e "${BOLD}${SECRET_NAME}${NC} — ${SECRET_DESC}"
    print_info "Exemplo: $SECRET_EXAMPLE"
    prompt "Cole o valor (não será exibido):"
    read -rs SECRET_VALUE
    echo ""

    if [ -z "$SECRET_VALUE" ]; then
        print_warn "Valor vazio. Pulando $SECRET_NAME..."
        return
    fi

    echo "$SECRET_VALUE" | gh secret set "$SECRET_NAME" --repo "$REPO" --body -
    print_ok "Secret $SECRET_NAME configurado!"
}

# -----------------------------------------------------------------------------
# Render.com — Secrets
# -----------------------------------------------------------------------------
print_step "Configurando secrets do Render.com..."
echo ""
echo -e "${BLUE}Como obter as credenciais do Render:${NC}"
echo "  1. Acesse https://render.com e faça login"
echo "  2. Para RENDER_API_KEY: Vá em Account Settings > API Keys > Create API Key"
echo "  3. Para RENDER_SERVICE_ID: Abra seu serviço > URL da página (o ID está na URL)"
echo "     Exemplo URL: https://dashboard.render.com/web/srv-XXXXXXXXXX → ID = srv-XXXXXXXXXX"
echo ""

set_secret "RENDER_API_KEY" \
    "API Key do Render.com para deploy automático" \
    "rnd_ABCDEFghijklmnop1234567890"

set_secret "RENDER_SERVICE_ID" \
    "ID do serviço backend no Render" \
    "srv-abc123def456"

# -----------------------------------------------------------------------------
# Banco de dados — Secret
# -----------------------------------------------------------------------------
print_step "Configurando secret do banco de dados..."
echo ""
echo -e "${BLUE}Como obter a DATABASE_URL do Render:${NC}"
echo "  1. No painel do Render, clique no seu banco de dados"
echo "  2. Vá em 'Info' > 'Connections'"
echo "  3. Copie a 'External Database URL' (começa com postgresql://)"
echo "     Formato: postgresql://user:password@hostname:5432/dbname"
echo ""

set_secret "DATABASE_URL" \
    "URL de conexão com PostgreSQL (do Render)" \
    "postgresql://gelateria_user:senha@oregon-postgres.render.com:5432/gelateria_xyz"

# -----------------------------------------------------------------------------
# Flask — Secret Key
# -----------------------------------------------------------------------------
print_step "Configurando SECRET_KEY do Flask..."
echo ""
echo -e "${BLUE}Gerar uma chave segura automaticamente?${NC}"
prompt "(S = gerar automático, N = inserir manualmente) [S/n]:"
read -r KEY_CHOICE

if [[ "${KEY_CHOICE,,}" != "n" ]]; then
    FLASK_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || \
                   openssl rand -hex 32 2>/dev/null || \
                   head -c 32 /dev/urandom | base64 | tr -d '=/+' | head -c 64)
    echo "$FLASK_SECRET" | gh secret set "SECRET_KEY" --repo "$REPO" --body -
    print_ok "SECRET_KEY gerada automaticamente e configurada!"
    print_info "Valor gerado (salve em local seguro): $FLASK_SECRET"
else
    set_secret "SECRET_KEY" \
        "Chave secreta do Flask (use uma string longa e aleatória)" \
        "a1b2c3d4e5f6...64chars..."
fi

# -----------------------------------------------------------------------------
# Vercel — Secrets
# -----------------------------------------------------------------------------
print_step "Configurando secrets do Vercel..."
echo ""
echo -e "${BLUE}Como obter as credenciais do Vercel:${NC}"
echo "  1. Acesse https://vercel.com e faça login"
echo ""
echo "  Para VERCEL_TOKEN:"
echo "    Vá em Account Settings > Tokens > Create Token"
echo ""
echo "  Para VERCEL_ORG_ID e VERCEL_PROJECT_ID:"
echo "    Opção A (CLI): Execute:  npx vercel link"
echo "      Depois: cat .vercel/project.json"
echo "    Opção B (painel): Abra seu projeto > Settings > General"
echo "      Scroll até 'Project ID' e 'Team ID'"
echo ""

set_secret "VERCEL_TOKEN" \
    "Token de autenticação do Vercel" \
    "aBcDeFgHiJkLmNoPqRsTuVwXyZ123456"

set_secret "VERCEL_ORG_ID" \
    "ID da organização/conta no Vercel (Team ID)" \
    "team_AbCdEfGhIjKlMnOp"

set_secret "VERCEL_PROJECT_ID" \
    "ID do projeto no Vercel" \
    "prj_AbCdEfGhIjKlMnOpQrStUvWx"

# -----------------------------------------------------------------------------
# Verificar secrets configurados
# -----------------------------------------------------------------------------
print_step "Verificando secrets configurados no repositório..."
echo ""
gh secret list --repo "$REPO"

# -----------------------------------------------------------------------------
# Resumo final
# -----------------------------------------------------------------------------
echo -e "\n${GREEN}"
echo "╔══════════════════════════════════════════════════╗"
echo "║     ✅ CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!      ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}📋 Próximos passos:${NC}"
echo ""
echo -e "  ${YELLOW}1.${NC} Faça push para a branch main para ativar o deploy automático:"
echo -e "     ${BLUE}git push origin main${NC}"
echo ""
echo -e "  ${YELLOW}2.${NC} Acompanhe o deploy em:"
echo -e "     ${BLUE}https://github.com/${REPO}/actions${NC}"
echo ""
echo -e "  ${YELLOW}3.${NC} Após o deploy, acesse:"
echo -e "     🌐 Frontend: ${BLUE}https://gelateria.vercel.app${NC}"
echo -e "     🔧 Backend:  ${BLUE}https://gelateria-backend.onrender.com${NC}"
echo ""
print_info "Consulte o README.md para instruções detalhadas"
