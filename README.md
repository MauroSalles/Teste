# 🍦 Gelateria CMD-Web — Guia Completo de Produção

> Sistema de gerenciamento de gelateria com interface estilo terminal CMD.  
> Deploy automático com **Render** (backend) + **Vercel** (frontend) + **GitHub Actions** (CI/CD).

[![Deploy Status](https://github.com/MauroSalles/Teste/actions/workflows/deploy.yml/badge.svg)](https://github.com/MauroSalles/Teste/actions/workflows/deploy.yml)
[![Frontend](https://img.shields.io/badge/Frontend-gelateria.vercel.app-black?logo=vercel)](https://gelateria.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-onrender.com-46E3B7?logo=render)](https://gelateria-backend.onrender.com)

---

## 📑 Índice

1. [🎯 Visão Geral](#-visão-geral)
2. [📋 Pré-requisitos](#-pré-requisitos)
3. [🔀 Merge dos PRs](#-merge-dos-prs)
4. [🐳 Setup Local com Docker](#-setup-local-com-docker)
5. [🌐 Deploy no Render (Backend)](#-deploy-no-render-backend)
6. [🎨 Deploy no Vercel (Frontend)](#-deploy-no-vercel-frontend)
7. [🔐 Configurar GitHub Secrets](#-configurar-github-secrets)
8. [🏁 Validação em Produção](#-validação-em-produção)
9. [🌍 Domínio Gratuito](#-domínio-gratuito)
10. [🛠️ Troubleshooting](#-troubleshooting)
11. [📁 Estrutura de Arquivos](#-estrutura-de-arquivos)
12. [📚 Recursos Úteis](#-recursos-úteis)

---

## 🎯 Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                  ARQUITETURA DO SISTEMA                  │
│                                                         │
│  👤 Usuário                                             │
│      │                                                  │
│      ▼                                                  │
│  🌐 VERCEL (Frontend)         📱 gelateria.vercel.app   │
│      │  HTML + CSS + JS                                 │
│      │  Interface CMD                                   │
│      │                                                  │
│      ▼ HTTP/HTTPS                                       │
│  🔧 RENDER (Backend)          🔧 gelateria-backend      │
│      │  Python + Flask                                  │
│      │  API REST                                        │
│      │                                                  │
│      ▼                                                  │
│  🗄️  RENDER (PostgreSQL)      🗄️  Banco de dados         │
│      └── sabores, pedidos,                              │
│          clientes, estoque                              │
│                                                         │
│  🔄 GITHUB ACTIONS            CI/CD automático          │
│      └── Testa → Deploy                                 │
│          a cada push em main                            │
└─────────────────────────────────────────────────────────┘
```

**URLs em produção:**
- 🌐 **Frontend**: `https://gelateria.vercel.app`
- 🔧 **Backend API**: `https://gelateria-backend.onrender.com`
- 📊 **CI/CD**: `https://github.com/MauroSalles/Teste/actions`

---

## 📋 Pré-requisitos

### Para rodar localmente:
- [Git](https://git-scm.com) (versão 2.x+)
- [Docker Desktop](https://docs.docker.com/get-docker/) (inclui Docker Compose)
- Navegador moderno (Chrome, Firefox, Edge)

### Para configurar em produção:
- Conta no [GitHub](https://github.com) (já tem ✅)
- Conta no [Render.com](https://render.com) (grátis)
- Conta no [Vercel](https://vercel.com) (grátis)
- [GitHub CLI](https://cli.github.com) (opcional, para setup automático)

### Para o script de configuração automática:
```bash
# Instalar GitHub CLI no Linux/WSL
sudo apt install gh

# Instalar no Mac
brew install gh

# Instalar no Windows
winget install GitHub.cli
```

---

## 🔀 Merge dos PRs

Antes de fazer o deploy, você precisa fazer o merge dos Pull Requests que contêm o código do sistema.

### Passo a passo:

**1. Acesse os Pull Requests do repositório:**

```
https://github.com/MauroSalles/Teste/pulls
```

**2. Abra o PR #1** — Sistema base (frontend + backend + banco de dados)

**3. Clique no botão verde "Merge pull request":**

```
┌────────────────────────────────────────────────┐
│  ✅ This branch has no conflicts with the base  │
│                                                │
│  [Merge pull request ▼]  [Close pull request]  │
└────────────────────────────────────────────────┘
```

**4. Clique em "Confirm merge"**

**5. Repita para o PR #2** — Configuração de deploy (Docker, CI/CD)

**6. Repita para este PR #3** — Guia de produção (README, scripts)

> ⚠️ **Importante**: Faça o merge na ordem correta: #1 → #2 → #3

### Verificar se o merge foi feito:

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
ls -la
# Deve aparecer: backend/, frontend/, docker-compose.yml, README.md, etc.
```

---

## 🐳 Setup Local com Docker

### Opção 1: Script automático (recomendado)

```bash
# Clonar o repositório
git clone https://github.com/MauroSalles/Teste.git
cd Teste

# Rodar o script de setup
bash setup-dev.sh
```

O script faz tudo automaticamente:
- Verifica pré-requisitos
- Cria o arquivo `.env`
- Sobe os containers Docker
- Aguarda o banco ficar pronto
- Executa as migrações

### Opção 2: Manual

**1. Clonar e entrar no repositório:**
```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
```

**2. Criar arquivo de variáveis:**
```bash
cp .env.example .env
# Edite o .env se necessário (as configurações padrão já funcionam localmente)
```

**3. Subir os containers:**
```bash
docker compose up -d
```

**4. Verificar se está rodando:**
```bash
docker compose ps
# Todos os serviços devem ter status "Up"

curl http://localhost:5000/health
# Deve retornar: {"status": "ok"}
```

**5. Acessar o sistema:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:5000
- 🗄️ PostgreSQL: localhost:5432

### Comandos úteis do Docker:

```bash
# Ver logs em tempo real
docker compose logs -f

# Ver logs só do backend
docker compose logs -f backend

# Reiniciar um serviço
docker compose restart backend

# Parar tudo (mantém os dados)
docker compose down

# Parar e apagar os dados do banco
docker compose down -v

# Reconstruir as imagens do zero
docker compose build --no-cache
docker compose up -d
```

---

## 🌐 Deploy no Render (Backend)

O Render hospeda o backend Flask e o banco de dados PostgreSQL.

### Passo 1: Criar conta no Render

1. Acesse **https://render.com**
2. Clique em **"Get Started for Free"**
3. Clique em **"Continue with GitHub"**
4. Autorize o Render a acessar seu GitHub
5. Confirme sua conta pelo email

### Passo 2: Criar banco de dados PostgreSQL

1. No painel do Render, clique em **"New +"**
2. Selecione **"PostgreSQL"**
3. Preencha:
   - **Name**: `gelateria-db`
   - **Database**: `gelateria`
   - **User**: `gelateria_user`
   - **Region**: `Oregon (US West)` ← mais próximo do Brasil no plano free
   - **Plan**: `Free` (90 dias grátis, depois ~$7/mês)
4. Clique em **"Create Database"**
5. **Copie a "External Database URL"** — você vai precisar dela!

```
postgresql://gelateria_user:SENHA@oregon-postgres.render.com:5432/gelateria_xyz
```

> 📌 Guarde essa URL! Ela será o valor do secret `DATABASE_URL` no GitHub.

### Passo 3: Criar Web Service (Backend)

1. No painel, clique em **"New +"**
2. Selecione **"Web Service"**
3. Clique em **"Connect a repository"**
4. Selecione **"MauroSalles/Teste"**
5. Preencha:
   - **Name**: `gelateria-backend`
   - **Region**: `Oregon (US West)`
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`
   - **Plan**: `Free`

### Passo 4: Configurar variáveis de ambiente no Render

Na seção **"Environment Variables"**, adicione:

| Variável | Valor |
|----------|-------|
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `0` |
| `SECRET_KEY` | _(gere uma chave aleatória forte)_ |
| `DATABASE_URL` | _(URL copiada no Passo 2)_ |
| `ALLOWED_ORIGINS` | `https://gelateria.vercel.app` |
| `PORT` | `10000` |

> Para gerar uma SECRET_KEY segura:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

### Passo 5: Deploy automático

1. Clique em **"Create Web Service"**
2. O Render vai fazer o build e deploy automaticamente
3. Aguarde o status ficar **"Live"** (3-5 minutos)
4. Acesse: `https://gelateria-backend.onrender.com/health`

### Obter o Service ID (para GitHub Actions):

1. Abra seu serviço no Render
2. Observe a URL: `https://dashboard.render.com/web/srv-XXXXXXXXXX`
3. O ID é: `srv-XXXXXXXXXX` → salve como `RENDER_SERVICE_ID`

### Obter a API Key do Render:

1. Clique no seu avatar (canto superior direito)
2. Vá em **"Account Settings"**
3. Clique em **"API Keys"**
4. Clique em **"Create API Key"**
5. Nomeie como `github-actions` e copie o valor → salve como `RENDER_API_KEY`

> ⚠️ **Plano Free do Render**: O serviço "dorme" após 15 minutos sem uso. A primeira requisição pode demorar 30-60 segundos para "acordar" o servidor. Isso é normal no plano gratuito.

---

## 🎨 Deploy no Vercel (Frontend)

O Vercel hospeda o frontend e gera automaticamente o subdomínio `gelateria.vercel.app`.

### Passo 1: Criar conta no Vercel

1. Acesse **https://vercel.com**
2. Clique em **"Sign Up"**
3. Selecione **"Continue with GitHub"**
4. Autorize o Vercel
5. Escolha **"Hobby"** (plano gratuito)

### Passo 2: Importar o projeto

1. No painel do Vercel, clique em **"Add New..."** → **"Project"**
2. Em **"Import Git Repository"**, localize **"MauroSalles/Teste"**
3. Clique em **"Import"**

### Passo 3: Configurar o projeto

Na tela de configuração:

- **Framework Preset**: Selecione conforme seu frontend (Vite, Next.js, etc.)
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist` (ou `build` dependendo do framework)

### Passo 4: Configurar variáveis de ambiente

Clique em **"Environment Variables"** e adicione:

| Variável | Valor |
|----------|-------|
| `VITE_API_URL` | `https://gelateria-backend.onrender.com` |

### Passo 5: Deploy

1. Clique em **"Deploy"**
2. Aguarde o build (1-2 minutos)
3. O Vercel gera automaticamente: `https://gelateria.vercel.app` (ou similar)

> 💡 **Dica**: O Vercel cria um preview deployment para cada Pull Request, permitindo testar mudanças antes do merge!

### Personalizar o subdomínio:

Por padrão, o Vercel usa o nome do projeto. Para ter `gelateria.vercel.app`:

1. Vá em **Project Settings** → **Domains**
2. O Vercel mostrará o domínio gerado (ex: `teste-mauro.vercel.app`)
3. Para mudar, clique em **"Edit"** e renomeie o projeto para `gelateria`

### Obter credenciais do Vercel (para GitHub Actions):

**Token:**
1. Vá em **Account Settings** → **Tokens**
2. Clique em **"Create"**
3. Nomeie como `github-actions`, escopo `Full Account`
4. Copie o token → salve como `VERCEL_TOKEN`

**Project ID e Org ID:**
```bash
# Na pasta do projeto, execute:
npx vercel link

# Depois leia o arquivo criado:
cat .vercel/project.json
# {"projectId":"prj_xxx","orgId":"team_xxx"}
```

Ou no painel: **Project Settings** → **General** → role até "Project ID"

---

## 🔐 Configurar GitHub Secrets

Os secrets são variáveis sensíveis que o GitHub Actions usa no deploy. **Nunca são expostos nos logs.**

### Opção 1: Script automático (recomendado)

```bash
# Instalar GitHub CLI se necessário
sudo apt install gh   # Linux
brew install gh       # Mac

# Autenticar
gh auth login

# Rodar o script
bash setup-production.sh
```

O script vai pedir cada valor e configurar automaticamente.

### Opção 2: Pelo painel do GitHub

1. Acesse: `https://github.com/MauroSalles/Teste/settings/secrets/actions`
2. Clique em **"New repository secret"** para cada secret abaixo:

| Secret | Onde obter | Exemplo |
|--------|-----------|---------|
| `DATABASE_URL` | Render → PostgreSQL → External URL | `postgresql://user:pass@host:5432/db` |
| `RENDER_API_KEY` | Render → Account Settings → API Keys | `rnd_ABC...` |
| `RENDER_SERVICE_ID` | URL do serviço no Render | `srv-ABC...` |
| `SECRET_KEY` | Gerar manualmente (veja abaixo) | String aleatória de 64 chars |
| `VERCEL_TOKEN` | Vercel → Account Settings → Tokens | `aBcD...` |
| `VERCEL_ORG_ID` | `.vercel/project.json` ou painel | `team_ABC...` |
| `VERCEL_PROJECT_ID` | `.vercel/project.json` ou painel | `prj_ABC...` |

### Gerar SECRET_KEY segura:

```bash
# Python (mais simples)
python3 -c "import secrets; print(secrets.token_hex(32))"

# OpenSSL
openssl rand -hex 32
```

### Verificar secrets configurados:

```bash
gh secret list --repo MauroSalles/Teste
```

Ou no GitHub: **Settings → Secrets and variables → Actions**

---

## 🏁 Validação em Produção

Após o deploy, verifique se tudo está funcionando:

### Checklist de validação:

```bash
# 1. Testar o backend (health check)
curl https://gelateria-backend.onrender.com/health
# Esperado: {"status": "ok", "database": "connected"}

# 2. Testar API de sabores
curl https://gelateria-backend.onrender.com/api/sabores
# Esperado: lista de sabores em JSON

# 3. Verificar frontend
curl -I https://gelateria.vercel.app
# Esperado: HTTP/2 200

# 4. Verificar HTTPS
curl -v https://gelateria-backend.onrender.com/health 2>&1 | grep "SSL"
# Esperado: SSL certificate verify OK
```

### Verificar o pipeline CI/CD:

1. Acesse: `https://github.com/MauroSalles/Teste/actions`
2. Veja o último workflow run
3. Todos os jobs devem estar com ✅ verde

### Acompanhar logs em produção:

**Render (Backend):**
1. Painel do Render → seu serviço → **"Logs"**
2. Logs em tempo real ficam disponíveis

**Vercel (Frontend):**
1. Painel do Vercel → seu projeto → **"Functions"** (para SSR)
2. Para sites estáticos, veja as **"Deployments"**

---

## 🌍 Domínio Gratuito

### Usar subdomínio gratuito (recomendado para começar)

Sem nenhuma configuração extra, você já tem:

| Serviço | URL Gratuita |
|---------|-------------|
| Vercel (Frontend) | `https://gelateria.vercel.app` |
| Render (Backend) | `https://gelateria-backend.onrender.com` |

**Essas URLs já vêm com HTTPS/SSL gratuito! ✅**

### Domínio `.com.br` barato (futuro)

Quando quiser um domínio profissional:

| Registrador | Preço médio | Site |
|-------------|------------|------|
| **Registro.br** | R$ 40/ano | [registro.br](https://registro.br) |
| **GoDaddy** | ~R$ 15-50/ano | [godaddy.com](https://godaddy.com) |
| **Namecheap** | ~R$ 15-40/ano | [namecheap.com](https://namecheap.com) |
| **Hostinger** | ~R$ 30/ano | [hostinger.com.br](https://hostinger.com.br) |

### Conectar domínio próprio ao Vercel:

1. **Comprar o domínio** no Registro.br ou similar

2. **Adicionar domínio no Vercel:**
   - Painel → Project → **Settings** → **Domains**
   - Clique **"Add"** → digite `gelateria.com.br`

3. **Configurar DNS no Registro.br:**
   - Adicione um registro **CNAME**: `www` → `cname.vercel-dns.com`
   - Ou registro **A**: `@` → `76.76.21.21` (IP do Vercel)

4. **Aguardar propagação**: 5 minutos a 48 horas

5. **SSL automático**: O Vercel configura HTTPS automaticamente!

---

## 🛠️ Troubleshooting

### ❌ Backend não responde (cold start)

**Problema**: A primeira requisição demora 30-60 segundos.

**Causa**: Plano gratuito do Render "dorme" após 15 min sem uso.

**Solução**:
```bash
# Fazer um "ping" antes de usar o sistema
curl https://gelateria-backend.onrender.com/health

# Ou usar um serviço de uptime (ex: UptimeRobot - gratuito)
# Configure para pingar a URL a cada 14 minutos
```

---

### ❌ Erro de CORS no frontend

**Problema**: `Access to fetch blocked by CORS policy`

**Solução**: Adicione a URL do frontend nas variáveis de ambiente do backend:
```bash
# No Render, atualize a variável:
ALLOWED_ORIGINS=https://gelateria.vercel.app,https://seu-dominio.com.br
```

---

### ❌ Deploy falhando no GitHub Actions

**Verificar**:
```bash
# Ver o log do workflow
gh run list --repo MauroSalles/Teste
gh run view <RUN_ID> --log
```

**Causas comuns**:
1. Secret não configurado → Verificar `Settings > Secrets`
2. RENDER_SERVICE_ID errado → Copiar da URL do Render
3. Build falhou → Verificar se `requirements.txt` está correto

---

### ❌ Banco de dados não conecta

**Verificar**:
```bash
# Testar conexão direta (substitua pelos seus dados)
psql "postgresql://user:senha@hostname:5432/dbname"

# Ou com Python
python3 -c "
import psycopg2
conn = psycopg2.connect('SUA_DATABASE_URL')
print('Conectado com sucesso!')
conn.close()
"
```

**Causas comuns**:
1. `DATABASE_URL` errada → Copiar novamente do painel do Render
2. Banco de dados pausado (plano free expira em 90 dias)
3. IP não permitido → Verificar `IP Allow List` no Render

---

### ❌ Vercel: erro no build

**Ver logs**:
1. Painel Vercel → Deployments → Clique no deployment com erro
2. Ou via CLI: `vercel logs`

**Causas comuns**:
1. `VITE_API_URL` não configurada → Adicionar em Environment Variables
2. Dependências faltando → Verificar `package.json`
3. Erro de build → Ver output completo nos logs

---

### ❌ Docker Compose não sobe localmente

```bash
# Ver logs de erro
docker compose logs

# Verificar se as portas estão livres
lsof -i :5000   # Backend
lsof -i :3000   # Frontend
lsof -i :5432   # PostgreSQL

# Se alguma porta estiver em uso, mate o processo:
kill $(lsof -t -i :5000)

# Reconstruir tudo do zero
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 📁 Estrutura de Arquivos

```
Teste/
├── 📄 README.md                    ← Este arquivo
├── 📄 .env.example                 ← Template de variáveis de ambiente
├── 📄 render.yaml                  ← Configuração do Render.com
├── 📄 vercel.json                  ← Configuração do Vercel
├── 📄 docker-compose.yml           ← Orquestração local com Docker
├── 📄 setup-dev.sh                 ← Script setup local
├── 📄 setup-production.sh          ← Script setup produção
│
├── 📁 .github/
│   └── 📁 workflows/
│       └── 📄 deploy.yml           ← Pipeline CI/CD (GitHub Actions)
│
├── 📁 backend/                     ← API Flask (Python)
│   ├── 📄 app.py                   ← Ponto de entrada da aplicação
│   ├── 📄 requirements.txt         ← Dependências Python
│   ├── 📄 Dockerfile               ← Imagem Docker do backend
│   ├── 📁 routes/                  ← Endpoints da API
│   │   ├── 📄 sabores.py
│   │   ├── 📄 pedidos.py
│   │   └── 📄 estoque.py
│   ├── 📁 models/                  ← Modelos do banco de dados
│   │   ├── 📄 sabor.py
│   │   ├── 📄 pedido.py
│   │   └── 📄 cliente.py
│   └── 📁 services/                ← Lógica de negócio
│       ├── 📄 gelateria_service.py
│       └── 📄 db_service.py
│
├── 📁 frontend/                    ← Interface CMD (HTML/CSS/JS)
│   ├── 📄 index.html               ← Página principal
│   ├── 📄 package.json             ← Dependências Node.js
│   ├── 📁 src/
│   │   ├── 📄 main.js              ← Lógica principal
│   │   ├── 📄 terminal.js          ← Simulação do terminal CMD
│   │   └── 📄 commands.js          ← Comandos disponíveis
│   └── 📁 styles/
│       └── 📄 terminal.css         ← Estilo CMD (fundo preto, texto verde)
│
└── 📁 database/                    ← Scripts SQL
    ├── 📄 schema.sql               ← Criar tabelas
    └── 📄 seed.sql                 ← Dados iniciais
```

---

## 📚 Recursos Úteis

### Documentação oficial:
- 🐍 **Flask**: https://flask.palletsprojects.com
- 🐘 **PostgreSQL**: https://www.postgresql.org/docs
- 🐳 **Docker**: https://docs.docker.com
- 🔧 **Render**: https://render.com/docs
- ⚡ **Vercel**: https://vercel.com/docs
- 🔄 **GitHub Actions**: https://docs.github.com/actions

### Ferramentas gratuitas:
- 📊 **UptimeRobot** (monitoramento): https://uptimerobot.com
- 🔍 **Sentry** (erros em produção): https://sentry.io
- 📈 **LogRocket** (sessões de usuário): https://logrocket.com
- 🔒 **Let's Encrypt** (SSL gratuito): https://letsencrypt.org

### Comandos rápidos:

```bash
# Setup local
bash setup-dev.sh

# Configurar secrets de produção
bash setup-production.sh

# Ver status dos containers
docker compose ps

# Ver logs em tempo real
docker compose logs -f

# Testar backend localmente
curl http://localhost:5000/health

# Testar backend em produção
curl https://gelateria-backend.onrender.com/health

# Ver status do último deploy
gh run list --repo MauroSalles/Teste --limit 5
```

---

<div align="center">

**🍦 Feito com ❤️ para a Gelateria**

*Sistema CMD-Web — Deploy automático com Render + Vercel + GitHub Actions*

</div>
