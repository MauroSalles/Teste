# 🍦 Gelateria Sistema — Projeto Integrador

[![CI](https://github.com/MauroSalles/Teste/actions/workflows/ci.yml/badge.svg)](https://github.com/MauroSalles/Teste/actions/workflows/ci.yml)

> **Projeto Integrador Acadêmico** — Sistema de Gerenciamento de Gelateria  
> MVP v1.0 com escopo definido e fechado. Veja [SCOPE.md](SCOPE.md) para os detalhes.

Sistema completo de gerenciamento de gelateria com interface CMD web, REST API, dashboard administrativo, autenticação JWT e sistema de fidelidade.

**Stack:** Python/Flask · PostgreSQL · HTML/CSS/JS (Vanilla)  
**Deploy:** Render.com (backend + PostgreSQL) · Vercel (frontend)

---

## 🎯 Escopo

Este é um **Projeto Integrador acadêmico** com escopo MVP definido. As funcionalidades implementadas no `main` estão listadas em [SCOPE.md](SCOPE.md). Features como WebSocket, pagamentos, IA/ML, AR, Redis, Nginx e multi-tenant estão **fora do escopo** desta versão.

---

## ✨ Features

| Área | Funcionalidades |
|------|----------------|
| 💻 **Terminal CMD** | Interface web tipo terminal com autocomplete, histórico e toasts |
| 🌐 **REST API** | Endpoints completos para sabores, pedidos, estoque e relatórios |
| 🔐 **Autenticação** | Registro, login com JWT, `/me` protegido, hashing scrypt |
| 📊 **Dashboard** | Painel admin com cards de resumo, tabela de pedidos e alertas de estoque |
| 📈 **Relatórios** | Vendas diárias/semanais/mensais e ranking de sabores |
| 📦 **Estoque Self-Service** | Inventário de freezers (açaí/sorvete), pedido semanal, registro de remessas |
| 🎯 **Fidelidade** | 10 pontos por item pedido, resgate a cada 100 pontos |
| 🎮 **Gamificação** | Badges e níveis por engajamento |
| 🔑 **Login** | Página de autenticação com JWT |
| 🛡️ **Admin** | Painel administrativo unificado |
| 🧪 **Testes** | 100+ testes automatizados (pytest) sem banco de dados real |
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
│   │   ├── estoque.py            # CRUD estoque (clássico)
│   │   ├── estoque_sabores.py    # Inventário self-service (açaí/sorvetes)
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
│   ├── estoque.html              # Painel self-service de estoque
│   ├── admin.html                # Painel admin unificado
│   ├── relatorios.html           # Relatórios e vendas
│   ├── login.html                # Página de autenticação
│   ├── script.js                 # Terminal logic
│   └── style.css                 # Dark terminal theme + CSS variables
├── database/
│   └── schema.sql                # PostgreSQL schema
├── tests/
│   ├── conftest.py
│   ├── test_api_routes.py        # REST API tests
│   ├── test_auth.py              # Auth flow tests
│   ├── test_cmd_service.py       # Command parser tests
│   └── test_gamification.py
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                # Lint + tests
│   │   └── deploy.yml            # Deploy to Render
│   └── branch-protection.md     # Política de proteção de branch
├── SCOPE.md                      # Escopo oficial do MVP v1.0
├── ROADMAP.md                    # Milestones e roadmap
├── CONTRIBUTING.md               # Guia de contribuição
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

> **Banco de dados:** Considere [Supabase](https://supabase.com) ou [Neon.tech](https://neon.tech) como alternativa ao PostgreSQL do Render (que expira em 90 dias no plano free).

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
| GET | `/api/pedidos` | Listar pedidos (paginação: `?page=&per_page=`) |
| POST | `/api/pedidos` | Criar pedido `{sabor_id, quantidade}` |
| PUT | `/api/pedidos/<id>` | Atualizar pedido |
| DELETE | `/api/pedidos/<id>` | Cancelar pedido |

### Estoque
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/estoque` | Ver estoque clássico |
| PUT | `/api/estoque/<sabor_id>` | Definir quantidade `{quantidade}` |
| GET | `/api/estoque/sabores` | Inventário self-service completo |
| GET | `/api/estoque/sabores/resumo` | Resumo com contagens e alertas |
| GET | `/api/estoque/faltando` | Sabores abaixo do mínimo |
| POST | `/api/estoque/pedido-semanal` | Registrar pedido semanal `{itens}` |
| POST | `/api/estoque/atualizar` | Registrar chegada de remessa `{itens}` |

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

### Relatórios & Outros
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/relatorios/sabores-populares?limit=5` | Top N sabores |
| GET | `/api/status` | Resumo geral do sistema |
| GET | `/health` | Health check |
| POST | `/cmd` | Interface CMD `{command: "listar sabores"}` |

---

## 🧪 Testes

```bash
pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests/ -v --tb=short
```

100+ testes — todos passam sem banco de dados real (mocks).

---

## 🤝 Como Contribuir

Consulte o [CONTRIBUTING.md](CONTRIBUTING.md) para o guia completo de contribuição, incluindo:

- Fluxo de Pull Requests obrigatório
- Política de review (≥1 aprovação)
- Labels e categorização de issues
- Como ativar branch protection

---

## 🏫 Projeto Integrador — Informações

- **Tipo:** Projeto Integrador Acadêmico (escopo MVP fechado)
- **Curso:** Tecnologia da Informação
- **Tema:** Sistema de Gerenciamento de Gelateria
- **Stack:** Python/Flask + PostgreSQL + HTML/CSS/JS Vanilla
- **Deploy:** Render.com + Vercel (zero custo)
- **Escopo:** [SCOPE.md](SCOPE.md) — MVP v1.0 definido e fechado
- **Roadmap:** [ROADMAP.md](ROADMAP.md) — Milestones e features futuras
