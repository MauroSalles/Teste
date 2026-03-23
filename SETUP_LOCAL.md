# 🛠️ SETUP LOCAL — Guia Completo de Configuração

> Siga este guia do início ao fim para ter o ambiente de desenvolvimento rodando na sua máquina.

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Clonar o repositório](#2-clonar-o-repositório)
3. [Configuração automática (recomendado)](#3-configuração-automática-recomendado)
4. [Configuração manual (passo a passo)](#4-configuração-manual-passo-a-passo)
5. [Variáveis de ambiente](#5-variáveis-de-ambiente)
6. [Banco de dados](#6-banco-de-dados)
7. [Rodar o backend](#7-rodar-o-backend)
8. [Rodar o frontend](#8-rodar-o-frontend)
9. [Testar a API](#9-testar-a-api)
10. [Hot reload e Debugging](#10-hot-reload-e-debugging)
11. [Comandos úteis](#11-comandos-úteis)

---

## 1. Pré-requisitos

Antes de começar, instale tudo que está listado em **[REQUISITOS.md](REQUISITOS.md)**.

Resumo rápido — você precisa ter instalado:

- ✅ Git 2.x+
- ✅ Python 3.9+
- ✅ Node.js 16+
- ✅ PostgreSQL 12+
- ✅ VS Code (recomendado)

Para verificar:

```bash
git --version
python3 --version   # ou python --version no Windows
node --version
psql --version
```

---

## 2. Clonar o repositório

```bash
# 1. Abra o Terminal (macOS/Linux) ou CMD/PowerShell (Windows)

# 2. Navegue até a pasta onde deseja salvar o projeto
cd ~/Documents   # macOS/Linux
cd %USERPROFILE%\Documents   # Windows CMD

# 3. Clone o repositório
git clone https://github.com/MauroSalles/Teste.git

# 4. Entre na pasta do projeto
cd Teste

# 5. Abra no VS Code
code .
```

---

## 3. Configuração automática (recomendado)

### macOS / Linux

```bash
# Dê permissão de execução ao script (apenas na primeira vez)
chmod +x setup.sh

# Execute o setup automático
./setup.sh
```

### Windows

```cmd
# No CMD ou PowerShell, dentro da pasta do projeto:
setup.bat
```

O script cuida de:
- Verificar Git, Python e Node.js
- Criar o ambiente virtual Python (`venv`)
- Instalar as dependências Python (`pip install -r requirements.txt`)
- Instalar dependências Node.js (se houver `package.json`)
- Criar o arquivo `.env` a partir do `.env.example`
- Avisar sobre próximos passos

Após o setup, siga para a seção [5. Variáveis de ambiente](#5-variáveis-de-ambiente).

---

## 4. Configuração manual (passo a passo)

Caso prefira fazer manualmente ou se o script encontrar algum problema:

### 4.1 Criar ambiente virtual Python

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

> Quando o venv estiver ativo, você verá `(venv)` no início do terminal.

### 4.2 Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 4.3 Instalar dependências Node.js (frontend)

```bash
# Se houver pasta frontend com package.json
cd frontend
npm install
cd ..
```

### 4.4 Criar arquivo .env

```bash
# macOS/Linux
cp .env.example .env

# Windows CMD
copy .env.example .env
```

---

## 5. Variáveis de ambiente

Edite o arquivo `.env` criado no passo anterior com seus dados reais:

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=gere-uma-chave-secreta-aleatoria

DB_HOST=localhost
DB_PORT=5432
DB_NAME=gelateria
DB_USER=postgres
DB_PASSWORD=sua_senha_do_postgres
DATABASE_URL=postgresql://postgres:sua_senha@localhost:5432/gelateria

ALLOWED_ORIGINS=http://localhost:3000
```

> ⚠️ **Nunca commite o arquivo `.env`** — ele já está no `.gitignore`.

---

## 6. Banco de dados

### 6.1 Iniciar PostgreSQL

```bash
# macOS (Homebrew)
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows — abra o pgAdmin ou vá em Gerenciamento do Computador
#           → Serviços → postgresql-x64-XX → Iniciar
```

### 6.2 Criar o banco de dados

```bash
# Conecte ao PostgreSQL
psql -U postgres

# Dentro do psql, crie o banco:
CREATE DATABASE gelateria;
\q
```

### 6.3 Executar migrations

```bash
# Certifique-se de que o venv está ativo
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Executar migrations (Alembic)
alembic upgrade head
```

> Se ainda não houver migrations, o backend cria as tabelas automaticamente ao iniciar.

---

## 7. Rodar o backend

```bash
# Ative o venv (se não estiver ativo)
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

# Inicie o servidor Flask
python backend/app.py
```

Ou use o script auxiliar:

```bash
./start-dev.sh
```

O backend estará disponível em: **http://localhost:5000**

Rotas principais:
- `GET  /` — Verifica se o servidor está rodando
- `GET  /api/sabores` — Lista sabores disponíveis
- `POST /api/pedidos` — Cria um novo pedido
- `GET  /api/estoque` — Consulta estoque

---

## 8. Rodar o frontend

```bash
# Navegue até a pasta do frontend
cd frontend

# Inicie o servidor de desenvolvimento
npm start
# ou
npm run dev
```

O frontend estará disponível em: **http://localhost:3000**

> Em outro terminal, certifique-se de que o backend também está rodando.

---

## 9. Testar a API

### Com Thunder Client (VS Code)

1. Instale a extensão **Thunder Client** no VS Code
2. Clique no ícone de raio na barra lateral
3. Crie uma nova requisição:
   - `GET http://localhost:5000/api/sabores`
4. Clique em **Send**

### Com curl (terminal)

```bash
# Verificar saúde do backend
curl http://localhost:5000/

# Listar sabores
curl http://localhost:5000/api/sabores

# Criar pedido (POST)
curl -X POST http://localhost:5000/api/pedidos \
  -H "Content-Type: application/json" \
  -d '{"sabor": "chocolate", "quantidade": 2}'
```

### Acessar pgAdmin

1. Instale o **pgAdmin**: https://www.pgadmin.org/download/
2. Abra no navegador (normalmente http://localhost/pgadmin4)
3. Conecte com:
   - Host: `localhost`
   - Port: `5432`
   - Database: `gelateria`
   - Username: `postgres`
   - Password: a que você definiu no `.env`

---

## 10. Hot reload e Debugging

### Hot reload automático (Flask)

Com `FLASK_DEBUG=1` no `.env`, o Flask reinicia automaticamente ao salvar qualquer arquivo Python. Não é necessária nenhuma configuração extra.

### Debugging com VS Code

Crie o arquivo `.vscode/launch.json` na raiz do projeto:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend Flask",
      "type": "debugpy",
      "request": "launch",
      "program": "${workspaceFolder}/backend/app.py",
      "envFile": "${workspaceFolder}/.env",
      "console": "integratedTerminal"
    }
  ]
}
```

Pressione **F5** para iniciar o debug. Você pode:
- Adicionar breakpoints clicando à esquerda do número da linha
- Inspecionar variáveis no painel **Variables**
- Usar o console de debug para executar expressões

---

## 11. Comandos úteis

```bash
# Ativar ambiente virtual
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Instalar nova dependência e atualizar requirements.txt
pip install nome-do-pacote
pip freeze > requirements.txt

# Rodar testes
pytest

# Ver logs em tempo real do Flask
FLASK_DEBUG=1 python backend/app.py

# Parar o servidor — pressione Ctrl+C no terminal onde ele está rodando

# Desativar ambiente virtual
deactivate
```

---

## 🆘 Precisando de ajuda?

- Consulte o arquivo **[REQUISITOS.md](REQUISITOS.md)** para instalar dependências
- Consulte **[TROUBLESHOOTING_VERCEL.md](TROUBLESHOOTING_VERCEL.md)** para problemas de deploy
- Abra uma [issue no GitHub](https://github.com/MauroSalles/Teste/issues)
