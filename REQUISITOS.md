# 📋 Pré-requisitos — Gelateria Sistema

Tudo que você precisa instalar **antes** de rodar o projeto localmente.

---

## ✅ Checklist Rápido

| Ferramenta | Versão Mínima | Como Verificar |
|---|---|---|
| Git | 2.30+ | `git --version` |
| Python | 3.12+ | `python --version` |
| pip | 23+ | `pip --version` |
| PostgreSQL | 14+ | `psql --version` |
| Node.js (opcional) | 18+ | `node --version` |
| Docker (opcional) | 24+ | `docker --version` |

---

## 🔧 Instalação por Sistema Operacional

### 🐧 Linux (Ubuntu/Debian)

```bash
# Git
sudo apt update && sudo apt install -y git

# Python 3.12
sudo apt install -y python3.12 python3.12-venv python3-pip

# PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Node.js (opcional, para servir o frontend)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Docker (opcional)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

### 🍎 macOS

```bash
# Homebrew (gerenciador de pacotes)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Git
brew install git

# Python 3.12
brew install python@3.12

# PostgreSQL
brew install postgresql@16
brew services start postgresql@16

# Node.js (opcional)
brew install node

# Docker Desktop (opcional)
# Baixe em: https://www.docker.com/products/docker-desktop
```

### 🪟 Windows

```powershell
# Git — https://git-scm.com/download/win
# Python 3.12 — https://www.python.org/downloads/
# PostgreSQL — https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
# Node.js — https://nodejs.org/
# Docker Desktop — https://www.docker.com/products/docker-desktop

# Ou com Winget:
winget install Git.Git
winget install Python.Python.3.12
winget install PostgreSQL.PostgreSQL
winget install OpenJS.NodeJS
```

---

## 🖥️ Extensões do VS Code Recomendadas

Instale pelo ID no VS Code (`Ctrl+P` → `ext install <id>`):

| Extensão | ID | Para quê |
|---|---|---|
| Python | `ms-python.python` | Suporte Python completo |
| Pylance | `ms-python.vscode-pylance` | IntelliSense Python |
| Python Debugger | `ms-python.debugpy` | Debug Python |
| SQLTools | `mtxr.sqltools` | Query no banco direto |
| SQLTools PostgreSQL | `mtxr.sqltools-driver-pg` | Driver PostgreSQL |
| GitLens | `eamodio.gitlens` | Git aprimorado |
| REST Client | `humao.rest-client` | Testar APIs |
| Docker | `ms-azuretools.vscode-docker` | Gerenciar containers |

---

## 🗄️ Configurar PostgreSQL Localmente

### Criar banco de dados

```bash
# Linux/macOS — logar como postgres
sudo -u postgres psql

# Windows — abrir PostgreSQL Shell (psql)
# Usuário padrão: postgres
```

```sql
-- Criar banco e usuário
CREATE DATABASE gelateria;
CREATE USER gelateria_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE gelateria TO gelateria_user;
\q
```

### Aplicar schema

```bash
psql -h localhost -U gelateria_user -d gelateria -f database/schema.sql
```

---

## 🐳 Alternativa: Docker (mais fácil)

Se você tem Docker instalado, pode pular toda a instalação de PostgreSQL:

```bash
# Iniciar banco com Docker
docker run -d \
  --name gelateria-db \
  -e POSTGRES_DB=gelateria \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=changeme \
  -p 5432:5432 \
  postgres:16-alpine

# Ou com docker-compose (já configurado no projeto)
docker-compose up -d db
```

---

## ✅ Verificação Final

Execute para confirmar que tudo está instalado:

```bash
git --version          # git version 2.x.x
python --version       # Python 3.12.x
pip --version          # pip 23.x.x
psql --version         # psql (PostgreSQL) 14.x ou 16.x
```

Se tudo aparecer, você está pronto para o [SETUP_LOCAL.md](SETUP_LOCAL.md)! 🚀
