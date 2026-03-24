# 🚀 Setup Local — Gelateria Sistema

Guia completo para rodar o projeto em sua máquina em **menos de 5 minutos**.

---

## ⚡ Setup Automático (recomendado)

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
./setup.sh
```

O script faz tudo: cria virtualenv, instala dependências, cria `.env`, aplica schema e inicia o servidor.

---

## 🔧 Setup Manual (passo a passo)

### 1. Clonar o repositório

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
```

### 2. Criar e ativar ambiente virtual Python

```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Windows (CMD)
.\.venv\Scripts\activate.bat
```

### 3. Instalar dependências Python

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais do banco:

```env
FLASK_ENV=development
PORT=5000

DB_HOST=localhost
DB_NAME=gelateria
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_PORT=5432

ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### 5. Criar banco de dados e aplicar schema

```bash
# Criar banco (se ainda não existir)
createdb gelateria

# Aplicar schema (tabelas + dados iniciais)
psql -h localhost -U postgres -d gelateria -f database/schema.sql
```

### 6. Iniciar o backend

```bash
python -m backend.app
# ou
flask --app backend.app run --debug
```

O backend estará disponível em: **http://localhost:5000**

Teste: `curl http://localhost:5000/health`

### 7. Abrir o frontend

```bash
# Opção 1: abrir direto no navegador
open frontend/index.html   # macOS
xdg-open frontend/index.html  # Linux

# Opção 2: servir com Python (necessário para Service Worker)
cd frontend && python3 -m http.server 5500
# Acesse: http://localhost:5500
```

---

## 🐳 Setup com Docker (alternativa)

```bash
# Iniciar todos os serviços
docker-compose up

# Em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

---

## ✅ Validar Setup

```bash
# 1. Health check do backend
curl http://localhost:5000/health
# Esperado: {"database":"ok","service":"gelateria-backend","status":"ok"}

# 2. Testar comando via API
curl -X POST http://localhost:5000/cmd \
  -H "Content-Type: application/json" \
  -d '{"comando": "listar sabores"}'

# 3. Rodar testes automatizados
pytest tests/ -v
```

---

## 🧪 Rodar Testes

```bash
# Todos os testes com cobertura
pytest tests/ -v --cov=backend --cov-report=term-missing

# Apenas testes de serviço
pytest tests/test_cmd_service.py -v

# Apenas testes de rotas
pytest tests/test_routes.py -v
```

---

## 🛑 Problemas Comuns

### `ModuleNotFoundError: No module named 'backend'`

Execute sempre na raiz do projeto (onde está `requirements.txt`), e com o virtualenv ativado:

```bash
cd Teste         # raiz do projeto
source .venv/bin/activate
python -m backend.app
```

### `psycopg2.OperationalError: could not connect to server`

Verifique se o PostgreSQL está rodando:

```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list | grep postgres

# Iniciar se parado
sudo systemctl start postgresql  # Linux
brew services start postgresql@16  # macOS
```

### `ALLOWED_ORIGINS is not set` (aviso no log)

Normal em desenvolvimento! Adicione ao `.env`:

```env
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### Frontend não conecta ao backend (CORS error)

Confirme que `ALLOWED_ORIGINS` no backend inclui a URL do seu frontend, e que o backend está rodando em `localhost:5000`.

---

## 📂 Estrutura de Arquivos

```
Teste/
├── backend/
│   ├── app.py              ← Ponto de entrada Flask (create_app)
│   ├── database.py         ← Pool de conexões PostgreSQL
│   ├── routes/
│   │   ├── cmd_routes.py   ← POST /cmd
│   │   └── health_routes.py← GET /health
│   ├── models/
│   │   ├── sabor.py        ← CRUD sabores
│   │   ├── pedido.py       ← CRUD pedidos
│   │   └── estoque.py      ← CRUD estoque
│   └── services/
│       └── cmd_service.py  ← Lógica de processamento de comandos
├── frontend/
│   ├── index.html          ← Interface CMD
│   ├── style.css           ← Estilos terminal verde
│   ├── script.js           ← Lógica frontend
│   ├── sw.js               ← Service Worker (offline)
│   └── manifest.json       ← PWA manifest
├── tests/
│   ├── conftest.py         ← Fixtures pytest
│   ├── test_cmd_service.py ← Testes unitários
│   └── test_routes.py      ← Testes de integração
├── database/
│   └── schema.sql          ← Schema PostgreSQL
├── .env.example            ← Template de configuração
├── requirements.txt        ← Dependências Python
├── Dockerfile              ← Container Docker
├── docker-compose.yml      ← Orquestração local
├── render.yaml             ← Deploy no Render.com
├── vercel.json             ← Deploy no Vercel
├── Makefile                ← Comandos simplificados
├── REQUISITOS.md           ← Pré-requisitos
├── SETUP_LOCAL.md          ← Este guia
└── KAIZEN.md               ← Documentação de otimizações
```

---

Pronto! Acesse **http://localhost:5500** no navegador e digite `ajuda` para começar. 🍦
