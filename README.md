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
| 🧪 **Testes** | 91 testes automatizados (pytest) sem banco de dados real |
| 🚀 **CI/CD** | GitHub Actions (lint + testes + health check blue/green) em push/PR |
| 🏳️ **Feature Flags** | Ativar/desativar módulos em runtime via env vars (`FEATURE_*=1`) |
| 🌍 **i18n** | Suporte a pt/en/es via `Accept-Language`; `DEFAULT_LANG` configurável |
| 🔑 **API Keys** | Chaves para parceiros externos (`X-API-Key`), sem redesploy |
| 🤝 **Parceiros / Marketplace** | Cadastro de parceiros com geração de API key automática |
| 🏪 **Portal de Franquias** | Solicitação e gerenciamento de unidades franqueadas |
| 🏷️ **Multi-tenant / White-label** | Toda a stack configurável por variáveis de ambiente para spin-offs |
| 📖 **OpenAPI 3.0** | Spec completa servida em `/api/docs`, importável no Postman/Insomnia |
| 🎯 **Onboarding automático** | Guia passo-a-passo em `/api/onboarding` (i18n, feature-aware) |
| ⚖️ **Dynamic Scaling** | Docker Compose replica hints + Render auto-restart + pool DB configurável |

---

## 🗂️ Estrutura do Projeto

```
├── backend/
│   ├── app.py                    # Flask app factory
│   ├── database.py               # Connection pool + DATABASE_URL
│   ├── feature_flags.py          # Feature toggles (FEATURE_*=1)
│   ├── i18n.py                   # Internationalization (pt/en/es)
│   ├── tenant.py                 # Multi-tenant / white-label config
│   ├── auth/
│   │   ├── jwt_handler.py        # JWT decorator + generate_token
│   │   └── api_key_handler.py    # X-API-Key decorator for public API
│   ├── models/
│   │   ├── sabor.py              # CRUD sabores
│   │   ├── pedido.py             # CRUD pedidos + relatórios
│   │   ├── estoque.py            # CRUD estoque
│   │   ├── user.py               # Auth model (scrypt hashing)
│   │   └── fidelidade.py         # Sistema de pontos
│   ├── routes/
│   │   ├── cmd_routes.py         # POST /cmd
│   │   ├── health_routes.py      # GET /health, /health/detailed
│   │   ├── api_routes.py         # REST API /api/*
│   │   ├── auth_routes.py        # Auth /api/auth/*
│   │   ├── gamification_routes.py
│   │   ├── partner_routes.py     # /api/partners, /api/franchises
│   │   ├── features_routes.py    # /api/features
│   │   ├── onboarding_routes.py  # /api/onboarding
│   │   └── openapi_routes.py     # /api/docs (OpenAPI 3.0)
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
│   └── schema.sql                # PostgreSQL schema (12 tabelas)
├── tests/
│   ├── conftest.py
│   ├── test_api_routes.py        # REST API tests
│   ├── test_auth.py              # Auth flow tests
│   ├── test_cmd_service.py       # Command parser tests
│   ├── test_ar_system.py
│   ├── test_gamification.py
│   └── test_expansion.py        # Feature flags, i18n, tenant, onboarding, docs
├── .github/workflows/
│   ├── ci.yml                    # Lint + tests
│   └── deploy.yml                # Deploy to Render + health-check (blue/green)
├── Dockerfile
├── docker-compose.yml            # Replica scaling + feature-flag env vars
├── render.yaml                   # Zero-downtime deploy config
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
- **Frontend:** http://localhost:3000
- **Dashboard:** http://localhost:3000/dashboard.html

### Escalar horizontalmente (Dynamic Scaling)

```bash
# 3 réplicas do backend atrás do mesmo compose network
BACKEND_REPLICAS=3 docker compose up --scale backend=3
```

### Sem Docker (modo dev)

```bash
pip install -r requirements.txt
# Configure o .env com DB_HOST, DB_NAME etc.
FLASK_ENV=development PYTHONPATH=. python backend/app.py
```

---

## 🏳️ Feature Flags

Ative módulos em runtime sem redeploy — apenas altere variáveis de ambiente:

| Flag | Env Var | Padrão | Descrição |
|------|---------|--------|-----------|
| MARKETPLACE | `FEATURE_MARKETPLACE=1` | `0` | Parceiros e marketplace |
| FRANCHISE_PORTAL | `FEATURE_FRANCHISE_PORTAL=1` | `0` | Portal de franquias |
| PUBLIC_API | `FEATURE_PUBLIC_API=1` | `0` | Autenticação por API key |
| I18N | `FEATURE_I18N=1` | `1` | Internacionalização |
| AB_TEST | `FEATURE_AB_TEST=1` | `0` | Experimentos A/B |
| SPIN_OFF | `FEATURE_SPIN_OFF=1` | `0` | Modo multi-tenant / white-label |

Consulte o estado em tempo real:

```bash
curl http://localhost:5000/api/features
```

---

## 🌍 Internacionalização (i18n)

A API respeita o header `Accept-Language` e responde em português, inglês ou espanhol:

```bash
curl -H "Accept-Language: en" http://localhost:5000/api/onboarding
curl -H "Accept-Language: es" http://localhost:5000/api/onboarding
```

Idioma padrão configurável via `DEFAULT_LANG=en` no `.env`.

---

## 🏷️ Multi-tenant / White-label (Spin-off)

A mesma imagem Docker pode rodar como produtos totalmente diferentes — basta sobrescrever vars de ambiente:

```bash
TENANT_ID=delivery_abc \
TENANT_NAME="Delivery ABC" \
TENANT_CURRENCY=USD \
TENANT_LOCALE=en_US \
docker compose up
```

---

## 🔑 API Pública (para integrações externas)

1. Cadastre um parceiro: `POST /api/partners` → recebe `api_key`
2. Use a chave em chamadas: `X-API-Key: gp_xxxxxxxxxx`
3. Configure chaves válidas: `PARTNER_API_KEYS=gp_key1,gp_key2`

Spec completa (Postman/Insomnia-ready):

```bash
curl http://localhost:5000/api/docs
```

---

## 🌐 Como fazer deploy (Render + Vercel)

### Backend + PostgreSQL → Render.com

1. Acesse [render.com](https://render.com) e conecte sua conta GitHub
2. **New → Blueprint** → selecione o repositório (o `render.yaml` já configura tudo)
3. Defina manualmente no dashboard do Render:
   - `ALLOWED_ORIGINS` = URL do seu frontend no Vercel
   - `BASE_URL` = URL do backend (ex: `https://gelateria-backend.onrender.com`)
   - Feature flags e API keys conforme necessário
4. Deploy com **zero downtime**: o Render só troca o tráfego após `/health` retornar 200

### Frontend → Vercel

1. Acesse [vercel.com](https://vercel.com) e conecte o repositório
2. **Root Directory:** `frontend`
3. Adicione a variável de ambiente `API_URL` = URL do backend no Render
4. Deploy!

> **Banco de dados grátis permanente:** Considere [Supabase](https://supabase.com) ou [Neon.tech](https://neon.tech) como alternativa ao PostgreSQL do Render (que expira em 90 dias no plano free).

---

## 📚 Documentação da API

> A spec OpenAPI 3.0 completa está em `GET /api/docs` — importe direto no Postman.

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

### Parceiros & Franquias *(FEATURE_MARKETPLACE / FEATURE_FRANCHISE_PORTAL)*
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/partners` | Listar parceiros |
| POST | `/api/partners` | Cadastrar parceiro `{name, email, plan?}` → retorna `api_key` |
| GET | `/api/partners/<id>` | Detalhe de parceiro |
| DELETE | `/api/partners/<id>` | Desativar parceiro |
| GET | `/api/franchises` | Listar franquias |
| POST | `/api/franchises` | Solicitar franquia `{name, owner_name, email, city?, country?}` |
| GET | `/api/franchises/<id>` | Detalhe de franquia |
| PATCH | `/api/franchises/<id>/status` | Atualizar status `{status: pending\|active\|suspended}` |

### Plataforma
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/features` | Estado de todos os feature flags |
| GET | `/api/features/<FLAG>` | Estado de um flag específico |
| GET | `/api/onboarding` | Guia de onboarding localizado (Accept-Language) |
| GET | `/api/docs` | Spec OpenAPI 3.0 (JSON) |
| GET | `/health` | Health check simples |
| GET | `/health/detailed` | Health check com DB + uptime |
| POST | `/cmd` | Interface CMD `{command: "listar sabores"}` |

---

## 🧪 Testes

```bash
pip install pytest
PYTHONPATH=. python -m pytest tests/ -v
```

91 testes — todos passam sem banco de dados real (mocks/fixtures).

---

## 🏗️ Arquitetura de Expansão

```
┌─────────────────────────────────────────────────────────┐
│                    Gelateria Pro Core                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Feature  │ │  i18n    │ │  Tenant  │ │ API Keys │  │
│  │  Flags   │ │ pt/en/es │ │ Config   │ │ (public) │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │              REST API (Flask blueprints)          │  │
│  │  sabores · pedidos · estoque · auth · gamif.      │  │
│  │  partners · franchises · features · onboarding    │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │PostgreSQL│ │  Docker  │ │ OpenAPI  │ │  CI/CD   │  │
│  │  (pool)  │ │ scaling  │ │  /docs   │ │blue/green│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
  Spin-off A                     Spin-off B
  delivery white-label           SaaS outro segmento
  (TENANT_ID=delivery_abc)       (TENANT_ID=bakery_pro)
  (FEATURE_MARKETPLACE=1)        (FEATURE_FRANCHISE_PORTAL=1)
```

**Roadmap de Expansão:**
- [ ] A/B testing engine (`FEATURE_AB_TEST`)
- [ ] Marketplace de gelaterias (multi-store)
- [ ] Webhooks para integrações externas
- [ ] SDK cliente (Python / JS) gerado a partir da spec OpenAPI
- [ ] Painel de administração de tenants
- [ ] Métricas Prometheus + Grafana dashboard
- [ ] Rate limiting por API key
- [ ] Cache Redis para endpoints de alta leitura

---

## 🏫 Projeto Integrador — Informações

- **Curso:** Tecnologia da Informação
- **Tema:** Sistema de Gerenciamento de Gelateria
- **Stack:** Python/Flask + PostgreSQL + HTML/CSS/JS Vanilla
- **Deploy:** Render.com + Vercel (zero custo)
