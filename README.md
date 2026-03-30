# 🍦 Gelateria Sistema — Projeto Integrador

Sistema completo de gerenciamento de gelateria com interface CMD web, REST API, dashboard administrativo, autenticação JWT e sistema de fidelidade.

**Stack:** Python/Flask · PostgreSQL · HTML/CSS/JS (Vanilla)  
**Deploy:** Render.com (backend + PostgreSQL) · Vercel (frontend)

---

## ✨ Features

| Área | Funcionalidades |
|------|----------------|
| 💻 **Terminal CMD** | Interface web tipo terminal com autocomplete, histórico, toasts e command palette (Ctrl+K) |
| 🌐 **REST API** | Endpoints completos para sabores, pedidos, estoque, relatórios e fidelidade |
| 🔐 **Autenticação** | Registro, login com JWT, `/me` protegido |
| 📊 **Dashboard** | Painel admin com cards de resumo, tabela de pedidos, gráfico de sabores populares e alertas de estoque |
| 📈 **Relatórios** | Vendas diárias/semanais/mensais e ranking de sabores |
| 🎯 **Fidelidade** | 10 pontos por item pedido, resgate a cada 100 pontos |
| 🎮 **Gamification** | Badges, níveis, spin-wheel, leaderboard, desafios diários |
| 🌙 **Dark/Light Mode** | Toggle de tema persistido em localStorage |
| 📱 **PWA** | Service worker para funcionamento offline |
| 🧪 **Testes** | 51 testes automatizados (pytest) sem banco de dados real |
| 🚀 **CI/CD** | GitHub Actions (lint + testes) em push/PR |

---

## 🗂️ Estrutura do Projeto

```
├── backend/
│   ├── app.py                    # Flask app factory
│   ├── database.py               # Connection pool + DATABASE_URL
│   ├── auth/
│   │   └── jwt_handler.py        # JWT decorator + generate_token
│   ├── models/
│   │   ├── sabor.py              # CRUD sabores
│   │   ├── pedido.py             # CRUD pedidos + relatórios
│   │   ├── estoque.py            # CRUD estoque
│   │   ├── user.py               # Auth model (scrypt hashing)
│   │   └── fidelidade.py         # Sistema de pontos
│   ├── routes/
│   │   ├── cmd_routes.py         # POST /cmd
│   │   ├── health_routes.py      # GET /health
│   │   ├── api_routes.py         # REST API /api/*
│   │   ├── auth_routes.py        # Auth /api/auth/*
│   │   └── gamification_routes.py
│   └── services/
│       └── cmd_service.py        # Command parser
├── frontend/
│   ├── index.html                # Terminal CMD web UI
│   ├── dashboard.html            # Admin dashboard
│   ├── script.js                 # Terminal logic
│   ├── style.css                 # Dark terminal theme + CSS variables
│   ├── manifest.json             # PWA manifest
│   └── sw.js                     # Service worker
├── database/
│   └── schema.sql                # PostgreSQL schema (9 tabelas)
├── tests/
│   ├── conftest.py
│   ├── test_api_routes.py        # REST API tests
│   ├── test_auth.py              # Auth flow tests
│   ├── test_cmd_service.py       # Command parser tests
│   ├── test_ar_system.py
│   └── test_gamification.py
├── .github/workflows/
│   ├── ci.yml                    # Lint + tests
│   └── deploy.yml                # Deploy to Render
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── vercel.json
```

---

## 🚀 Como rodar localmente

### Pré-requisitos
- Docker e Docker Compose

### 1. Clone e configure o `.env`

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
cp .env.example .env
# Edite .env se necessário
```

### 2. Suba os contêineres

```bash
docker-compose up --build
```

- **Backend:** http://localhost:5000
- **Frontend:** http://localhost:8080
- **Dashboard:** http://localhost:8080/dashboard.html

### Sem Docker (modo dev)

```bash
pip install -r requirements.txt
# Configure o .env com DB_HOST, DB_NAME etc.
FLASK_ENV=development PYTHONPATH=. python backend/app.py
```

---

## 🌐 Como fazer deploy (Render + Vercel)

### Backend + PostgreSQL → Render.com

1. Acesse [render.com](https://render.com) e conecte sua conta GitHub
2. **New → Blueprint** → selecione o repositório (o `render.yaml` já configura tudo)
3. Defina manualmente no dashboard do Render:
   - `ALLOWED_ORIGINS` = URL do seu frontend no Vercel
4. Após o deploy, copie a URL do backend (ex: `https://gelateria-backend.onrender.com`)

### Frontend → Vercel

1. Acesse [vercel.com](https://vercel.com) e conecte o repositório
2. **Root Directory:** `frontend`
3. Adicione a variável de ambiente `API_URL` = URL do backend no Render
4. Deploy!

> **Banco de dados grátis permanente:** Considere [Supabase](https://supabase.com) ou [Neon.tech](https://neon.tech) como alternativa ao PostgreSQL do Render (que expira em 90 dias no plano free).

---

## 📚 Documentação da API

### Sabores
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/sabores` | Listar todos os sabores |
| POST | `/api/sabores` | Criar sabor `{nome, preco}` |
| PUT | `/api/sabores/<id>` | Atualizar sabor `{nome?, preco?}` |
| DELETE | `/api/sabores/<id>` | Remover sabor |

### Pedidos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/pedidos` | Listar pedidos |
| POST | `/api/pedidos` | Criar pedido `{sabor_id, quantidade}` |

### Estoque
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/estoque` | Ver estoque |
| PUT | `/api/estoque/<sabor_id>` | Definir quantidade `{quantidade}` |

### Relatórios
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/relatorios/vendas?periodo=diario` | Vendas por período (diario/semanal/mensal) |
| GET | `/api/relatorios/sabores-populares?limit=5` | Top N sabores por pedidos |
| GET | `/api/status` | Resumo geral do sistema |

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register` | Registrar `{name, email, password}` |
| POST | `/api/auth/login` | Login `{email, password}` → JWT |
| GET | `/api/auth/me` | Dados do usuário logado (Bearer token) |

### Fidelidade
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/fidelidade/<user_id>/pontos` | Consultar pontos |
| POST | `/api/fidelidade/<user_id>/resgatar` | Resgatar recompensa (100 pts) |

### Outros
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| POST | `/cmd` | Interface CMD `{command: "listar sabores"}` |

---

## 🧪 Testes

```bash
pip install pytest
PYTHONPATH=. python -m pytest tests/ -v
```

51 testes — todos passam sem banco de dados real (mocks).

---

## 📸 Screenshots

| Terminal CMD | Dashboard |
|:---:|:---:|
| Interface web tipo terminal verde | Painel admin com cards e gráficos |

---

## 🏫 Projeto Integrador — Informações

- **Curso:** Tecnologia da Informação
- **Tema:** Sistema de Gerenciamento de Gelateria
- **Stack:** Python/Flask + PostgreSQL + HTML/CSS/JS Vanilla
- **Deploy:** Render.com + Vercel (zero custo)
