# Roadmap — Gelateria Sistema

> **Projeto Integrador Acadêmico** — Sistema de Gerenciamento de Gelateria  
> Stack: Python/Flask · PostgreSQL · HTML/CSS/JS Vanilla

---

## 🏁 Milestone v1.0 — Projeto Integrador

**Status: ✅ CONCLUÍDO**  
**Data de conclusão:** Abril 2026  
**Branch:** `main`

### Features implementadas e PRs merged

| PR | Título | Área |
|----|--------|------|
| #22 | REST API, Auth JWT, Dashboard, Loyalty, PWA, Tests, CI | Core do sistema |
| #24 | Documentação e error handling | Qualidade |
| #32 | Health check detalhado, validações de auth, hardening JWT | Segurança |
| #37 | Inventário self-service de sabores (estoque) | Estoque |
| #38 | PR status survey | Documentação |
| #39 | Gestão de pedidos, API de estoque, painel admin, relatórios | Admin/Relatórios |
| #40 | Fix XSS, error handling, testes faltando, página de login | Segurança/Auth |

### Funcionalidades entregues no v1.0

- ✅ Interface web tipo terminal CMD
- ✅ REST API completa: sabores, pedidos, estoque, relatórios
- ✅ Autenticação JWT (registro, login, `/me`)
- ✅ Dashboard administrativo com cards e gráficos
- ✅ Sistema de fidelidade (10 pts/item, resgate a 100 pts)
- ✅ Gamificação (badges, níveis, leaderboard)
- ✅ Gestão de estoque self-service (freezers açaí/sorvete)
- ✅ Painel de relatórios (vendas diárias/semanais/mensais)
- ✅ Página de login com JWT
- ✅ Painel admin unificado
- ✅ Proteção XSS em todas as páginas frontend
- ✅ 100+ testes automatizados (pytest, sem banco real)
- ✅ CI/CD (GitHub Actions: lint + testes)
- ✅ Deploy: Render.com + Vercel

---

## 🔮 Milestone v2.0 — Pós-Entrega (Futuro)

**Status: 💡 PLANEJADO — apenas após conclusão do Projeto Integrador**

Funcionalidades que *poderiam* ser consideradas se o projeto evoluir para além do contexto acadêmico:

| Feature | Justificativa | Complexidade |
|---------|---------------|--------------|
| Notificações por email | Confirmação de pedidos, alertas de estoque | Média |
| Relatórios exportáveis (PDF/CSV) | Uso gerencial real | Baixa |
| Múltiplos usuários/perfis | Operadores diferentes (caixa, estoque, gerente) | Média |
| PWA completo com push notifications | Melhor experiência mobile | Média |
| Dashboard com gráficos avançados | Análise de tendências de vendas | Baixa |
| Cache básico (in-memory) | Performance em consultas frequentes | Baixa |

> ⚠️ Nenhuma feature do v2.0 deve ser implementada antes da entrega do Projeto Integrador.

---

## ❌ PRs Fora de Escopo — A Fechar

Os seguintes PRs estão abertos mas são **fora do escopo do MVP** e devem ser fechados pelo mantenedor:

| PR | Título | Motivo |
|----|--------|--------|
| #13 | Stripe, PIX, PayPal | Integração de pagamentos fora do escopo |
| #14 | IA + ML (chatbot, forecasting, churn) | Complexidade muito além do MVP acadêmico |
| #15 | Notification engine (email, SMS, push, WebSocket) | Infraestrutura externa fora do escopo |
| #17 | Loyalty System referral | Duplica sistema de pontos já implementado |
| #18 | Instagram, WhatsApp & AR social commerce | Feature experimental irrelevante para o MVP |
| #23 | [WIP] Clean up repository | Substituído por este PR |
| #25 | Gelateria Pro (WebSocket, Pagamentos, IA, Loyalty) | Feature creep massivo — múltiplos escopos |
| #26 | Landing page, /health/detailed, status page | Fora do escopo do MVP |
| #27 | Consolidate PR #25 + #26 | Consolida PRs fora de escopo |
| #28 | Gelateria Pro v3.0 | Feature creep — múltiplas features fora de escopo |
| #29 | Gelateria Pro v4.0 "Presence First" | Feature creep — social, viral, mascote |
| #30 | Feedback API, sabor do dia, cardápio nutricional | Fora do escopo do Projeto Integrador |
| #31 | micro-inovações: /health/detailed, tab-completion | Duplica features já implementadas |
| #33 | Redis caching layer, nginx reverse proxy | Infraestrutura de produção fora do escopo |
| #34 | Gelateria Pro v4.0 "Presence First" (Gelinho, Streak) | Feature creep — social consumer fora do escopo |
| #35 | Feature flags, i18n, multi-tenant, OpenAPI | Enterprise features fora do escopo acadêmico |
| #36 | Cache layer, analytics API, reviews system, nginx | Infraestrutura complexa fora do escopo |

**Para fechar os PRs acima**, acesse cada um no GitHub e:
1. Adicione um comentário: *"Fechando este PR pois está fora do escopo do MVP v1.0 do Projeto Integrador. Consulte [SCOPE.md](../SCOPE.md) para o escopo oficial. Features desta categoria podem ser consideradas em um Milestone v2.0 após a entrega acadêmica."*
2. Clique em **Close Pull Request**

---

## 🐛 Issues Abertas (Priorizadas)

> **Nota:** Não há issues abertas ativas no momento. As 18 issues listadas no histórico foram todas tratadas via PRs merged.

### Como criar novas issues

Use as labels definidas em [CONTRIBUTING.md](CONTRIBUTING.md):

| Tipo | Label | Quando usar |
|------|-------|-------------|
| Bug | `bug` | Comportamento incorreto no código atual do `main` |
| Melhoria | `enhancement` | Melhoria de feature já no escopo (ver SCOPE.md) |
| Documentação | `documentation` | README, comentários, docstrings |
| Fora de escopo | `out-of-scope` | Feature interessante mas fora do MVP v1.0 |
| Duplicado | `duplicate` | Issue/PR já existe |
| Em progresso | `wip` | Trabalho iniciado mas incompleto |

---

## 📚 Referências

- [SCOPE.md](SCOPE.md) — Escopo oficial do MVP v1.0
- [CONTRIBUTING.md](CONTRIBUTING.md) — Como contribuir
- [README.md](README.md) — Visão geral do sistema
