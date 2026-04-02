# 🍦 Gelateria Pro

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

Sistema profissional de gerenciamento de gelateria com API REST, dashboard em tempo real, pagamentos, IA, fidelidade e notificações.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Nginx)                   │
│  index.html (Terminal)   dashboard.html (Dashboard)     │
│  js/chatbot-widget.js    js/loyalty-widget.js           │
│  js/payment-widget.js                                   │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼──────────────────────────────┐
│                   Backend (Flask + SocketIO)             │
│                                                         │
│  /api/*          /api/payments/*   /api/ai/*            │
│  /api/loyalty/*  /api/notifications/*  /auth/*          │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Models  │  │ Services │  │ Realtime │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
└───────┼─────────────┼─────────────┼──────────────────────┘
        │             │             │
┌───────▼─────┐  ┌────▼────┐  ┌────▼────┐
│  PostgreSQL │  │  Redis  │  │ Ext APIs│
│  (dados)    │  │(cache)  │  │Stripe   │
└─────────────┘  └─────────┘  │SendGrid │
                               │OpenAI   │
                               └─────────┘
```

---

## 🚀 Quick Start (Docker)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/gelateria-pro.git
cd gelateria-pro

# 2. Configure as variáveis de ambiente
cp .env.example .env   # edite com suas chaves

# 3. Suba todos os serviços
docker compose up --build

# 4. Acesse
#   Frontend:  http://localhost:3000
#   API:       http://localhost:5000/health
#   Dashboard: http://localhost:3000/dashboard.html
```

---

## 🌐 Deploy em Produção

### Render.com (Backend + PostgreSQL)
1. Crie um novo **Web Service** apontando para este repositório
2. Configure `Build Command`: `pip install -r requirements.txt`
3. Configure `Start Command`: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app`
4. Adicione um **PostgreSQL** managed database e copie `DATABASE_URL`
5. Preencha as variáveis de ambiente (ver tabela abaixo)

### Vercel (Frontend)
1. Importe o repositório no Vercel
2. Configure `Root Directory`: `frontend`
3. Defina `window.API_URL` como a URL do seu backend no Render

---

## 📡 API Reference

| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/health` | — | Health check |
| GET | `/api/sabores` | — | Listar sabores |
| POST | `/api/sabores` | — | Criar sabor |
| GET | `/api/pedidos` | — | Listar pedidos |
| POST | `/api/pedidos` | — | Criar pedido |
| GET | `/api/estoque` | — | Ver estoque |
| PUT | `/api/estoque/<id>` | — | Atualizar estoque |
| POST | `/auth/register` | — | Registrar usuário |
| POST | `/auth/login` | — | Login (retorna JWT) |
| POST | `/api/payments/stripe/intent` | JWT | Criar payment intent |
| POST | `/api/payments/pix/qrcode` | JWT | Gerar QR PIX |
| GET | `/api/payments/pix/status/<txid>` | JWT | Status PIX |
| GET | `/api/payments/methods` | — | Métodos disponíveis |
| POST | `/api/ai/chat` | — | Chatbot |
| GET | `/api/ai/recommendations` | — | Recomendações |
| POST | `/api/ai/sentiment` | — | Análise de sentimento |
| GET | `/api/loyalty/referral/<id>` | JWT | Código de referral |
| POST | `/api/loyalty/coupon/validate` | JWT | Validar cupom |
| GET | `/api/loyalty/points/<id>` | JWT | Ver pontos |
| GET/POST | `/api/notifications/preferences` | JWT | Preferências |

---

## ⚙️ Variáveis de Ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `DATABASE_URL` | ✅ | URL de conexão PostgreSQL |
| `JWT_SECRET_KEY` | ✅ | Segredo para tokens JWT |
| `ALLOWED_ORIGINS` | ✅ | URLs permitidas pelo CORS |
| `STRIPE_SECRET_KEY` | ⚡ | Chave secreta Stripe |
| `STRIPE_WEBHOOK_SECRET` | ⚡ | Segredo do webhook Stripe |
| `SENDGRID_API_KEY` | ⚡ | Chave SendGrid para emails |
| `SENDGRID_FROM_EMAIL` | ⚡ | Email remetente |
| `OPENAI_API_KEY` | ⚡ | Chave OpenAI para chatbot |
| `REDIS_URL` | ⚡ | URL do Redis |
| `FLASK_ENV` | — | `production` ou `development` |

> ✅ Obrigatória · ⚡ Opcional (feature degradará graciosamente se ausente)

---

## 🛠️ Tech Stack

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.12, Flask 3.x, Flask-SocketIO |
| Banco de Dados | PostgreSQL 16, psycopg2 |
| Cache / Filas | Redis 7 |
| Autenticação | JWT (PyJWT) |
| Pagamentos | Stripe, PIX (mock) |
| IA / ML | OpenAI GPT, TextBlob, NumPy, scikit-learn |
| Email | SendGrid |
| PDF | ReportLab |
| Frontend | HTML5, CSS3, Vanilla JS, Socket.IO |
| Infra | Docker, Docker Compose, Gunicorn |
| Deploy | Render.com (backend), Vercel (frontend) |
| Testes | pytest, pytest-cov |
| Linting | flake8 |

---

## 🧪 Testes

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar todos os testes
PYTHONPATH=. pytest tests/ -v --cov=backend

# Apenas testes de pagamento
PYTHONPATH=. pytest tests/test_payments.py -v

# Linting crítico
flake8 backend --count --select=E9,F63,F7,F82
```

---

## 👥 Autores

- **Seu Nome** — [@seu-usuario](https://github.com/seu-usuario)

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
