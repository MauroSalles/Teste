# 🚀 Setup Local — Gelateria Sistema

Guia passo a passo para rodar o projeto localmente em **5 minutos**.

---

## ⚡ Setup Automático (recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/MauroSalles/Teste.git
cd Teste

# 2. Rode o script de setup (Linux/macOS)
./setup.sh

# 3. Configure o banco de dados
createdb gelateria
psql -d gelateria -f database/schema.sql

# 4. Inicie o backend
source .venv/bin/activate
python -m flask run

# 5. Abra o frontend
# Abra frontend/index.html no navegador
```

```batch
REM Windows:
setup.bat
```

---

## 🔧 Setup Manual (passo a passo)

### Passo 1 — Clone o repositório

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
```

### Passo 2 — Ambiente virtual Python

```bash
# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### Passo 3 — Instalar dependências

```bash
pip install -r requirements.txt
```

### Passo 4 — Variáveis de ambiente

```bash
cp .env.example .env
# Edite .env com suas credenciais de banco
```

Conteúdo mínimo do `.env`:

```env
DB_HOST=localhost
DB_NAME=gelateria
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_PORT=5432
FLASK_ENV=development
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
```

### Passo 5 — Banco de dados

```bash
# Criar banco
createdb gelateria

# Aplicar schema + seed
psql -d gelateria -f database/schema.sql
```

**Alternativa com Docker:**

```bash
docker compose up -d
# Aguardar ~10s e executar:
docker compose exec postgres psql -U postgres -d gelateria -f /docker-entrypoint-initdb.d/schema.sql
```

### Passo 6 — Iniciar backend

```bash
source .venv/bin/activate  # se não estiver ativado
python -m flask run
# Backend disponível em http://localhost:5000
```

### Passo 7 — Abrir frontend

Abra `frontend/index.html` diretamente no navegador, ou use um servidor local:

```bash
# Python (recomendado)
cd frontend && python3 -m http.server 5500
# Acesse: http://localhost:5500

# VS Code: extensão "Live Server" (botão "Go Live" na barra inferior)
```

---

## 🧪 Rodar Testes

```bash
# Ativar ambiente virtual primeiro
source .venv/bin/activate

# Configurar banco de testes
createdb gelateria_test
psql -d gelateria_test -f database/schema.sql

# Variáveis para testes
export DB_NAME=gelateria_test
export DB_PASSWORD=sua_senha

# Executar testes
pytest tests/ -v

# Com cobertura de código
pytest tests/ -v --cov=backend --cov-report=term-missing
```

---

## 🔍 Verificar se está funcionando

```bash
# Health check da API
curl http://localhost:5000/health

# Resposta esperada:
# {"status": "ok", "service": "gelateria-backend", "checks": {"database": "ok"}}

# Testar um comando
curl -X POST http://localhost:5000/cmd \
  -H "Content-Type: application/json" \
  -d '{"comando": "ajuda"}'
```

---

## 📁 Estrutura do Projeto

```
Teste/
├── backend/              # Flask API
│   ├── app.py            # Aplicação principal
│   ├── database.py       # Connection pool PostgreSQL
│   ├── models/           # Modelos de dados
│   ├── routes/           # Endpoints HTTP
│   └── services/         # Lógica de negócio
├── frontend/             # Interface web
│   ├── index.html        # Página principal
│   ├── style.css         # Estilos (dark/light mode)
│   ├── script.js         # Lógica do terminal
│   ├── manifest.json     # PWA manifest
│   └── sw.js             # Service Worker
├── database/
│   └── schema.sql        # Schema + seed data
├── tests/                # Testes automatizados
├── .env.example          # Template de variáveis
├── requirements.txt      # Dependências Python
├── docker-compose.yml    # Docker local
├── Dockerfile            # Container do backend
├── render.yaml           # Deploy Render
└── vercel.json           # Deploy Vercel
```

---

## ❓ Problemas Comuns

### `ALLOWED_ORIGINS` — erro de CORS
Adicione a URL do frontend no `.env`:
```env
ALLOWED_ORIGINS=http://localhost:5500
```

### Erro de conexão ao banco
1. Verifique se o PostgreSQL está rodando: `pg_isready`
2. Confirme as credenciais no `.env`
3. Teste conexão: `psql -h localhost -U postgres -d gelateria`

### `ModuleNotFoundError: No module named 'backend'`
Execute a partir da raiz do projeto com o ambiente virtual ativado:
```bash
source .venv/bin/activate
python -m flask run  # não: python backend/app.py
```

### Testes falhando com erro de banco
Crie o banco de testes separado:
```bash
createdb gelateria_test
export DB_NAME=gelateria_test
pytest tests/ -v
```
