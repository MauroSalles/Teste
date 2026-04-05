# Escopo Oficial — MVP v1.0 — Projeto Integrador

> **Gelateria Sistema** — Sistema de Gerenciamento de Gelateria  
> Projeto Integrador Acadêmico · Stack: Python/Flask · PostgreSQL · HTML/CSS/JS Vanilla

Este documento define o escopo **oficial e fechado** do MVP v1.0 entregue como Projeto Integrador.

---

## ✅ IN SCOPE — Funcionalidades implementadas no `main`

As seguintes funcionalidades estão **implementadas, testadas e deployadas**:

| Área | Descrição | Status |
|------|-----------|--------|
| 💻 **Interface Terminal CMD** | Interface web tipo terminal com histórico de comandos, autocomplete e toasts | ✅ Implementado |
| 🌐 **REST API — Sabores** | CRUD completo: GET/POST/PUT/DELETE `/api/sabores` | ✅ Implementado |
| 🌐 **REST API — Pedidos** | GET/POST `/api/pedidos` com paginação | ✅ Implementado |
| 🌐 **REST API — Estoque** | GET/PUT `/api/estoque`, endpoints self-service | ✅ Implementado |
| 🌐 **REST API — Relatórios** | Vendas diárias/semanais/mensais, top sabores | ✅ Implementado |
| 🔐 **Autenticação JWT** | Registro, login, `/me` protegido, hashing scrypt | ✅ Implementado |
| 📊 **Dashboard Administrativo** | Cards de resumo, tabela de pedidos, gráficos, alertas | ✅ Implementado |
| 📦 **Gestão de Estoque Self-Service** | Inventário de freezers, pedido semanal, registro de remessas | ✅ Implementado |
| 📈 **Painel de Relatórios** | Vendas e ranking de sabores com visualização | ✅ Implementado |
| 🎯 **Sistema de Fidelidade (Pontos)** | 10 pts por item, resgate a cada 100 pts | ✅ Implementado |
| 🎮 **Gamificação** | Badges, níveis, leaderboard | ✅ Implementado |
| 🔑 **Página de Login** | UI de autenticação com JWT | ✅ Implementado |
| 🛡️ **Painel Admin** | Gestão de sabores e pedidos integrada | ✅ Implementado |
| 🧪 **Testes Automatizados** | Suite pytest com mocks (sem DB real) | ✅ 100+ testes |
| 🚀 **CI/CD** | GitHub Actions: lint + testes em push/PR | ✅ Configurado |
| 🐳 **Containerização** | Dockerfile + docker-compose.yml | ✅ Configurado |
| ☁️ **Deploy** | Render.com (backend+DB) + Vercel (frontend) | ✅ Configurado |

---

## ❌ OUT OF SCOPE — Fora do Projeto Integrador

As funcionalidades abaixo **não fazem parte do MVP** e **não serão aceitas** em PRs para o branch `main`:

| Área | Motivo da Exclusão |
|------|-------------------|
| 🔌 **WebSocket em tempo real** | Infraestrutura complexa desnecessária para MVP acadêmico |
| 💳 **Integração de pagamentos** (Stripe, PIX, PayPal) | Fora do domínio do sistema de gelateria escolar |
| 🤖 **IA/ML** (chatbot, forecasting, churn, segmentação) | Complexidade muito além do escopo do Projeto Integrador |
| 📱 **AR Commerce** (Instagram, WhatsApp, realidade aumentada) | Feature experimental sem valor para o MVP |
| 🗄️ **Redis / Nginx** | Infraestrutura de produção além do escopo acadêmico |
| 🌍 **Multi-tenant, i18n, OpenAPI público** | Escalabilidade empresarial fora do escopo |
| 👥 **"Presence First" / social feed / mascote Gelinho** | Features de produto consumer sem relação com o projeto |
| 🔗 **Sistema de referral / cupons** | Lógica de negócio avançada além do MVP |
| 📧 **Engine de notificações** (email, SMS, push) | Integração externa fora do escopo |
| 🏢 **Feature flags / onboarding dinâmico** | Gerenciamento de produto enterprise |
| 📊 **Sistema de reviews/avaliações** | Feature secundária não solicitada no Projeto Integrador |

---

## 🎯 Critério de Aceite

Uma feature é **aceitável no MVP** se:

1. Resolve diretamente o problema de **gerenciamento de gelateria**
2. Não requer infraestrutura externa além de Flask + PostgreSQL
3. Pode ser testada com mocks sem banco de dados real
4. Não adiciona dependências externas pagas ou proprietárias
5. Está coberta por testes automatizados

---

## 📚 Documentos Relacionados

- [CONTRIBUTING.md](CONTRIBUTING.md) — Como contribuir com o projeto
- [ROADMAP.md](ROADMAP.md) — Milestones e funcionalidades futuras
- [README.md](README.md) — Visão geral do sistema
