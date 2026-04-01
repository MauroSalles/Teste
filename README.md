# 🍦 Gelateria Pro — Sistema de Gerenciamento de Gelateria

Sistema completo de gerenciamento de gelateria com interface CMD web, REST API, pagamentos, IA conversacional, programa de fidelidade, cupons e notificações em tempo real.

**Stack:** Python/Flask · PostgreSQL · Flask-SocketIO · HTML/CSS/JS (Vanilla)  
**Deploy:** Render.com (backend + PostgreSQL) · Vercel (frontend)

[![CI](https://github.com/MauroSalles/Teste/actions/workflows/ci.yml/badge.svg)](https://github.com/MauroSalles/Teste/actions/workflows/ci.yml)

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
| 💳 **Pagamentos** | Stripe (cartão de crédito/débito) e PIX com fallback mock para dev |
| 🏷️ **Cupons** | Sistema com 9 etapas de validação: uso único, cap diário/mensal, valor mínimo, desconto máximo |
| 📣 **Indicações** | Programa de referral com tiers Bronze / Silver / Gold e pontos de bônus |
| 🤖 **IA Chatbot** | Atendimento virtual em português; usa OpenAI GPT-3.5 se configurado, fallback inteligente |
| 📊 **Recomendações** | Engine de recomendação de sabores baseada no histórico de pedidos |
| 💬 **Análise de Sentimento** | Análise keyword-based em português para avaliações de clientes |
| 📧 **Notificações** | E-mails transacionais via SendGrid com fallback de log para dev |
| ⚡ **Tempo Real** | Flask-SocketIO emite eventos de novos pedidos, atualização de estoque e dashboard |
| 🌙 **Dark/Light Mode** | Toggle de tema persistido em localStorage |
| 📱 **PWA** | Service worker para funcionamento offline |
| 🧪 **Testes** | Testes automatizados (pytest) sem banco de dados real |
| 🚀 **CI/CD** | GitHub Actions (lint + testes) em push/PR |

---

## 🗂️ Estrutura do Projeto

```
├── backend/
│   ├── app.py                        # Flask app factory + SocketIO init
│   ├── database.py                   # Connection pool + DATABASE_URL
│   ├── auth/
│   │   └── jwt_handler.py            # JWT decorator + generate_token
│   ├── models/
│   │   ├── sabor.py                  # CRUD sabores
│   │   ├── pedido.py                 # CRUD pedidos + relatórios
│   │   ├── estoque.py                # CRUD estoque
│   │   ├── user.py                   # Auth model (scrypt hashing)
│   │   ├── fidelidade.py             # Sistema de pontos
│   │   └── payment.py                # Registro e atualização de pagamentos
│   ├── routes/
│   │   ├── cmd_routes.py             # POST /cmd
│   │   ├── health_routes.py          # GET /health
│   │   ├── api_routes.py             # REST API /api/*
│   │   ├── auth_routes.py            # Auth /api/auth/*
│   │   ├── gamification_routes.py    # Gamification /api/gamification/*
│   │   ├── payment_routes.py         # Pagamentos /api/payments/*
│   │   ├── ai_routes.py              # IA /api/ai/*
│   │   ├── loyalty_routes.py         # Fidelidade /api/loyalty/*
│   │   └── notification_routes.py    # Notificações /api/notifications/*
│   ├── payments/
│   │   ├── stripe_service.py         # Stripe PaymentIntent + webhook
│   │   └── pix_service.py            # Mock PIX QR code + status
│   ├── ai/
│   │   ├── chatbot_service.py        # Chatbot (OpenAI + fallback)
│   │   ├── recommendation_engine.py  # Recomendações por histórico
│   │   └── sentiment_service.py      # Análise de sentimento em PT
│   ├── loyalty/
│   │   ├── referral_service.py       # Código de indicação + tiers
│   │   └── coupon_service.py         # Cupons com validação 9 etapas
│   ├── notifications/
│   │   └── email_service.py          # SendGrid + fallback de log
│   ├── realtime/
│   │   └── socket_events.py          # Flask-SocketIO eventos
│   ├── gamification/
│   │   ├── gamification_engine.py
│   │   └── leaderboard.py
│   └── services/
│       └── cmd_service.py            # Command parser
├── frontend/
│   ├── index.html                    # Terminal CMD web UI
│   ├── dashboard.html                # Admin dashboard
│   ├── script.js                     # Terminal logic
│   ├── style.css                     # Dark terminal theme + CSS variables
│   ├── manifest.json                 # PWA manifest
│   └── sw.js                         # Service worker
├── database/
│   └── schema.sql                    # PostgreSQL schema (16 tabelas)
├── tests/
│   ├── conftest.py
│   ├── test_api_routes.py
│   ├── test_auth.py
│   ├── test_cmd_service.py
│   ├── test_ar_system.py
│   └── test_gamification.py
├── .github/workflows/
│   ├── ci.yml                        # Lint + tests
│   └── deploy.yml                    # Deploy to Render
├── Dockerfile
├── docker-compose.yml
├── render.yaml
└── vercel.json
```

---

## 🚀 Como rodar localmente

### Pré-requisitos
- Docker e Docker Compose  
  **ou** Python 3.11+ e PostgreSQL

### 1. Clone e configure o `.env`

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
cp .env.example .env   # ajuste as variáveis conforme necessário
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
FLASK_ENV=development PYTHONPATH=. python backend/app.py
```

---

## ⚙️ Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|:-----------:|-----------|
| `DATABASE_URL` | ✅ | URL de conexão PostgreSQL |
| `JWT_SECRET` | ✅ | Segredo para assinar tokens JWT |
| `ALLOWED_ORIGINS` | ✅ prod | Origens CORS permitidas (separadas por vírgula) |
| `FLASK_ENV` | — | `development` ou `production` (padrão) |
| `PORT` | — | Porta do servidor (padrão: 5000) |
| `STRIPE_SECRET_KEY` | — | Chave secreta Stripe (fallback mock se ausente) |
| `STRIPE_WEBHOOK_SECRET` | — | Segredo do webhook Stripe |
| `SENDGRID_API_KEY` | — | API key SendGrid (fallback log se ausente) |
| `SENDGRID_FROM_EMAIL` | — | E-mail remetente SendGrid |
| `OPENAI_API_KEY` | — | API key OpenAI para chatbot (fallback predefined se ausente) |

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
3. Adicione a variável `API_URL` = URL do backend no Render
4. Deploy!

> **Banco de dados grátis permanente:** Considere [Supabase](https://supabase.com) ou [Neon.tech](https://neon.tech) como alternativa ao PostgreSQL do Render (expira em 90 dias no plano free).

---

## 📚 Documentação da API

### Sabores
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| GET | `/api/sabores` | — | Listar todos os sabores |
| POST | `/api/sabores` | — | Criar sabor `{nome, preco}` |
| PUT | `/api/sabores/<id>` | — | Atualizar sabor |
| DELETE | `/api/sabores/<id>` | — | Remover sabor |

### Pedidos
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| GET | `/api/pedidos` | — | Listar pedidos |
| POST | `/api/pedidos` | — | Criar pedido `{sabor_id, quantidade}` |

### Estoque
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| GET | `/api/estoque` | — | Ver estoque |
| PUT | `/api/estoque/<sabor_id>` | — | Definir quantidade `{quantidade}` |

### Autenticação
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| POST | `/api/auth/register` | — | Registrar `{name, email, password}` |
| POST | `/api/auth/login` | — | Login → JWT |
| GET | `/api/auth/me` | JWT | Dados do usuário logado |

### Pagamentos
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| GET | `/api/payments/methods` | — | Métodos disponíveis |
| POST | `/api/payments/stripe/intent` | JWT | Criar PaymentIntent `{amount_cents, pedido_id?}` |
| POST | `/api/payments/stripe/webhook` | — | Webhook Stripe |
| POST | `/api/payments/pix/qrcode` | JWT | Gerar QR PIX `{value, pedido_id?, description?}` |
| GET | `/api/payments/pix/status/<txid>` | — | Consultar status PIX |

### IA
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| POST | `/api/ai/chat` | — | Chatbot `{message, user_id?}` |
| GET | `/api/ai/recommendations` | — | Recomendações `?user_id=&limit=3` |
| POST | `/api/ai/sentiment` | — | Análise de sentimento `{text}` |

### Fidelidade & Cupons
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| GET | `/api/loyalty/referral/<user_id>` | JWT | Stats de indicação + tier |
| POST | `/api/loyalty/referral/register` | JWT | Registrar uso de código `{code}` |
| POST | `/api/loyalty/coupon/validate` | JWT | Validar cupom `{code, order_value}` |
| POST | `/api/loyalty/coupon/apply` | JWT | Aplicar cupom `{code, order_value}` |

### Notificações
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| POST | `/api/notifications/send` | JWT | Enviar e-mail `{to, subject, body}` |
| POST | `/api/notifications/order-confirmation` | JWT | Confirmação de pedido |

### Utilitários
| Método | Endpoint | Auth | Descrição |
|--------|----------|:----:|-----------|
| GET | `/health` | — | Health check |
| POST | `/cmd` | — | Interface CMD `{command: "listar sabores"}` |

---

## ⚡ Eventos WebSocket (Socket.IO)

| Evento | Direção | Payload | Descrição |
|--------|---------|---------|-----------|
| `connected` | Server → Client | `{status: "ok"}` | Confirmação de conexão |
| `pedido_novo` | Server → Client | objeto pedido | Novo pedido criado |
| `estoque_atualizado` | Server → Client | objeto estoque | Estoque modificado |
| `dashboard_atualizado` | Server → Client | objeto métricas | Atualização do dashboard |

---

## 🗄️ Banco de Dados

O schema (`database/schema.sql`) define 16 tabelas:

| Tabela | Descrição |
|--------|-----------|
| `users` | Usuários do sistema |
| `sabores` | Catálogo de sabores |
| `pedidos` | Pedidos realizados |
| `estoque` | Controle de estoque |
| `fidelidade` | Pontos de fidelidade |
| `payments` | Registro de pagamentos |
| `referral_codes` | Códigos de indicação |
| `referral_conversions` | Histórico de indicações |
| `coupons` | Cupons de desconto |
| `coupon_usage_log` | Log de uso de cupons |
| `chat_logs` | Histórico do chatbot |
| `reviews` | Avaliações de sabores |
| `notification_log` | Log de notificações |
| `badges` | Badges de gamification |
| `user_badges` | Badges atribuídos a usuários |
| `missions` | Missões e desafios diários |

---

## 🧪 Testes

```bash
pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests/ -v
```

Todos os testes rodam sem banco de dados real (mocks/fixtures).

---

## 📸 Screenshots

| Terminal CMD | Dashboard |
|:---:|:---:|
| Interface web tipo terminal verde | Painel admin com cards e gráficos |

---

## 🏫 Informações do Projeto

- **Curso:** Tecnologia da Informação  
- **Tema:** Sistema de Gerenciamento de Gelateria  
- **Stack:** Python/Flask · PostgreSQL · Flask-SocketIO · HTML/CSS/JS Vanilla  
- **Deploy:** Render.com + Vercel (zero custo)
