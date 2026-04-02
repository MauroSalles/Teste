# 🩺 Diagnóstico Completo — Gelateria Pro (`main`)

> Gerado em 2026-04-02 | Branch: `main`

---

## 1. O que já foi implementado

### 🗄️ Banco de Dados (`database/schema.sql`)
- [x] Tabela `sabores` — id, nome, preço
- [x] Tabela `pedidos` — id, sabor_id (FK), quantidade, data
- [x] Tabela `estoque` — id, sabor_id (FK unique), quantidade
- [x] Tabela `users` — id, name, email, password_hash, avatar_url, level, total_points, deleted_at, created_at
- [x] Tabela `referral_conversions` — sistema de indicações
- [x] Tabela `user_badges` — badges do usuário (JSONB)
- [x] Tabela `daily_challenges` — desafios diários (JSONB)
- [x] Tabela `wheel_spins` — histórico da roleta
- [x] Tabela `fidelidade` — pontos e resgates por usuário
- [x] Seed data (5 sabores iniciais)
- [x] Pool de conexões PostgreSQL (`ThreadedConnectionPool`) com context manager

### 🔧 Backend (`backend/`)

#### Autenticação (`auth/jwt_handler.py`, `routes/auth_routes.py`)
- [x] Registro de usuários com hash de senha scrypt (N=16384, r=8, p=1, salt 16 bytes)
- [x] Login com `secrets.compare_digest` (tempo constante)
- [x] JWT HS256 com expiração de 24h (`PyJWT`)
- [x] Decorator `@token_required` para rotas protegidas
- [x] `GET /api/auth/me` para perfil autenticado
- [x] Validação de e-mail (regex) e senha mínima de 8 caracteres
- [x] Aviso de log se `JWT_SECRET_KEY` < 32 bytes

#### API REST (`routes/api_routes.py`)
- [x] `GET/POST /api/sabores` — listar e criar sabores
- [x] `PUT/DELETE /api/sabores/<id>` — atualizar preço e remover
- [x] `GET/POST /api/pedidos` — listar e criar pedidos
- [x] `GET /api/estoque` — ver estoque atual
- [x] `PUT /api/estoque/<id>` — definir quantidade em estoque
- [x] `GET /api/status` — dashboard resumido (receita total, alertas de estoque)
- [x] `GET /api/relatorios/vendas?periodo=diario|semanal|mensal`
- [x] `GET /api/relatorios/sabores-populares?limit=N`
- [x] `GET /api/fidelidade/<user_id>/pontos`
- [x] `POST /api/fidelidade/<user_id>/resgatar`

#### Gamificação (`routes/gamification_routes.py`, `gamification/`)
- [x] Badges: award, listar (`/api/gamification/badges`)
- [x] Níveis: progressão baseada em `total_points` (`/api/gamification/level`)
- [x] Desafios diários gerados dinamicamente (`/api/gamification/challenges/daily`)
- [x] Roleta de recompensas diária (`/api/gamification/spin`)
- [x] Leaderboard global e semanal (público)
- [x] Rank do usuário autenticado
- [x] Eventos sazonais (Natal, Halloween, etc.)

#### AR (`ar/ar_system.py`, `routes/gamification_routes.py`)
- [x] Criação de modelo 3D AR por sabor (`POST /api/gamification/ar/create`)
- [x] Try-on múltiplos sabores em AR (`POST /api/gamification/ar/try-on`)

#### Health Check (`routes/health_routes.py`)
- [x] `GET /health` — verificação básica de liveness
- [x] `GET /health/detailed` — status do DB, JWT, uptime (retorna 503 se DB offline)

#### Terminal CMD (`routes/cmd_routes.py`, `services/cmd_service.py`)
- [x] `POST /cmd` com 15+ comandos de texto: `listar sabores`, `add sabor`, `fazer pedido`, `ver estoque`, `set estoque`, `status`, `ajuda`, `limpar`, etc.

### 🌐 Frontend (`frontend/`)
- [x] `index.html` — terminal web (interface CMD estilo hacker)
- [x] `dashboard.html` — painel administrativo básico
- [x] `style.css` — tema dark/light com CSS variables
- [x] `script.js` — lógica do terminal + chamadas API
- [x] `sw.js` — service worker (cache offline para PWA)
- [x] `manifest.json` — configuração PWA (ícone, nome, cores)

### 🧪 Testes (`tests/`)
- [x] 55 testes automatizados (pytest + mocks, sem banco real)
- [x] `test_api_routes.py` — 14 testes das rotas REST
- [x] `test_auth.py` — 11 testes de registro, login e /me
- [x] `test_health.py` — 3 testes de health check básico e detalhado
- [x] `test_cmd_service.py` — 5 testes do parser de comandos
- [x] `test_gamification.py` — 16 testes de gamificação e leaderboard
- [x] `test_ar_system.py` — 5 testes do sistema AR

### 🚀 Infra / DevOps
- [x] `Dockerfile` — imagem Python com Gunicorn
- [x] `docker-compose.yml` — backend + PostgreSQL
- [x] `render.yaml` — deploy automático no Render.com
- [x] `vercel.json` — deploy do frontend na Vercel
- [x] `.github/workflows/ci.yml` — CI: lint (flake8) + pytest
- [x] `.github/workflows/deploy.yml` — CD para Render
- [x] `.env.example` — variáveis de ambiente documentadas
- [x] `CORS` configurável por env (`ALLOWED_ORIGINS`)

---

## 2. Checklist — O que está faltando ou merece refinamento

### 🗄️ Banco de Dados
- [ ] **`pedidos.user_id`** — pedidos não têm vínculo com o usuário que pediu (campo ausente no schema)
- [ ] **Índices** — falta índice em `pedidos.data`, `users.email`, `user_badges.user_id` para queries de relatório
- [ ] **Migrações** — sem sistema de migrations (Alembic/Flyway); schema só via `schema.sql`
- [ ] **Soft delete** em `sabores` — um sabor removido cascada em pedidos/estoque; falta `deleted_at`

### 🔒 Segurança
- [ ] **Rate limiting** — sem proteção contra brute-force em `/api/auth/login` e `/api/auth/register`
- [ ] **JWT revogação** — tokens não podem ser invalidados (sem blacklist/refresh token)
- [ ] **Input sanitization XSS** — frontend injeta HTML de respostas do servidor diretamente no DOM (`innerHTML`)
- [ ] **HTTPS enforcement** — sem redirecionamento HTTP→HTTPS em produção

### 🌐 Frontend
- [ ] **Páginas prometidas ausentes** — `landing.html`, `cardapio.html`, `delivery.html`, `ranking.html`, `analytics.html`, `kiosk.html`, `status.html` não existem no repositório
- [ ] **Formulário de registro/login** — ausente; autenticação só via API (sem UI)
- [ ] **Página de perfil do usuário** — ausente
- [ ] **Integração gamificação no frontend** — badges, level e leaderboard não são exibidos

### ⚡ Performance
- [ ] **Paginação** — `GET /api/pedidos` e `GET /api/sabores` retornam todos os registros sem limite/offset
- [ ] **Cache** — nenhum cache para endpoints de leitura frequente (`/api/status`, `/api/sabores`)

### 🧪 Testes
- [ ] **Cobertura de gamification routes** (HTTP) — `test_gamification.py` testa a engine diretamente, não os endpoints HTTP
- [ ] **Teste de integração com DB real** — CI não executa migrations e testes com PostgreSQL real
- [ ] **Teste do endpoint `/cmd`** — `test_cmd_service.py` testa a função, não a rota HTTP

### 📄 Documentação
- [ ] **OpenAPI/Swagger** — sem especificação de API pública
- [ ] **README detalhado** — setup local, variáveis de ambiente e exemplos de chamada

---

## 3. Sugestões e Micro-inovações

### ⚡ Incrementais (imediato — próximo sprint)

| # | Sugestão | Impacto | Esforço |
|---|----------|---------|---------|
| 1 | **Paginação** em `GET /api/pedidos` e `GET /api/sabores` (`?page=1&limit=20`) | Alto | Baixo |
| 2 | **Rate limiting** com `Flask-Limiter` (10 req/min em `/api/auth/*`) | Alto | Baixo |
| 3 | **Refresh token** — emitir `access_token` (15min) + `refresh_token` (7d) | Alto | Médio |
| 4 | **Índices no banco** — `CREATE INDEX` em `pedidos.data`, `users.email` | Alto | Baixo |
| 5 | **`pedidos.user_id`** — adicionar FK para rastrear pedidos por usuário | Alto | Médio |
| 6 | **Página de login/cadastro** (`login.html`) — formulário simples com fetch API | Alto | Médio |
| 7 | **Sanitização XSS** — substituir `innerHTML` por `textContent` onde não há HTML intencional | Alto | Baixo |
| 8 | **Migrações** — adicionar Alembic para versionamento do schema | Médio | Médio |
| 9 | **Cache in-memory** — `functools.lru_cache` ou `cachetools.TTLCache` para `/api/sabores` | Médio | Baixo |
| 10 | **OpenAPI spec** — `flask-smorest` ou `flasgger` para documentação automática | Médio | Médio |

### 🚀 Disruptivos (inovação forte — roadmap futuro)

| # | Sugestão | Conceito |
|---|----------|---------|
| 1 | **Sabor do Dia com IA** — GPT-4 gera descrição criativa do sabor do dia às 00h, postada automaticamente | Conteúdo gerado por IA |
| 2 | **Check-in com Streak** — usuário faz check-in diário ganhando XP; calendário estilo GitHub contributions | Ritual de hábito |
| 3 | **Feed Social** — clientes postam fotos do sorvete, curtidas e comentários em tempo real (WebSocket) | Rede social leve |
| 4 | **Mascote "Gelinho" 🍦** — chat bot emocional que aparece após 30s de inatividade, responde perguntas e sugere sabores | Companheiro virtual |
| 5 | **Clube de Assinatura** — planos Bronze/Prata/Ouro com desconto mensal e benefícios exclusivos | Receita recorrente |
| 6 | **Modo Kiosk** — tela fullscreen para autoatendimento em tablet na loja, sem necessidade de funcionário | Automação presencial |
| 7 | **QR Code de Mesa** — cada mesa tem QR único; cliente escaneia, escolhe e paga sem garçom | UX zero-fricção |
| 8 | **Cupom de aniversário automático** — cron job que envia cupom 3 dias antes do aniversário do cliente | CRM automatizado |
| 9 | **Analytics público** — painel estilo Vercel Analytics com heatmap de pedidos por hora/dia (sem auth) | Transparência + viralidade |
| 10 | **PWA com push notifications** — notificar cliente quando sabor favorito entra em estoque | Reconquista de cliente |

---

## 4. Bugs e Pontos Frágeis — Soluções

### 🐛 Bug: XSS via `innerHTML` no frontend

**Onde:** `frontend/script.js` — respostas do servidor são inseridas com `innerHTML`

**Risco:** Caso a API retorne conteúdo malicioso (ou seja comprometida), scripts injetados executariam no browser do cliente.

**Solução:** Usar `textContent` para conteúdo de texto puro; usar `DOMParser` ou sanitização (DOMPurify) para HTML intencional.

---

### 🐛 Bug: Status endpoint — lookup O(N²) *(já corrigido neste PR)*

**Onde:** `backend/routes/api_routes.py` — função `status()`

**Problema:** Para cada pedido, fazia varredura linear em todos os sabores para encontrar o preço.

**Solução aplicada:** `preco_por_nome = {s["nome"]: float(s["preco"]) for s in sabores}` — lookup O(1) com dict.

---

### 🐛 Bug: JWT secret key curta *(já corrigido neste PR)*

**Onde:** `backend/auth/jwt_handler.py`

**Problema:** O padrão era `"change-me-in-production"` (23 bytes), abaixo dos 32 bytes mínimos recomendados pelo RFC 7518 para HS256.

**Solução aplicada:** Padrão de 32 chars + aviso de log se a key for curta em produção.

---

### 🐛 Bug: Sem validação de formato de e-mail *(já corrigido neste PR)*

**Onde:** `backend/routes/auth_routes.py` — endpoint `/api/auth/register`

**Problema:** Qualquer string era aceita como e-mail (ex: `"notanemail"`).

**Solução aplicada:** Validação com regex `^[^@\s]+@[^@\s]+\.[^@\s]+$` antes de inserir no banco.

---

### ⚠️ Ponto frágil: Sem rate limiting em autenticação

**Onde:** `POST /api/auth/login`

**Risco:** Permite ataques de força bruta sem qualquer throttling.

**Solução sugerida:**
```python
# requirements.txt: Flask-Limiter>=3.5.0
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(get_remote_address, app=app, default_limits=["200/day"])

@auth_bp.post("/login")
@limiter.limit("10/minute")
def login(): ...
```

---

### ⚠️ Ponto frágil: Sem paginação nas listagens

**Onde:** `GET /api/pedidos`, `GET /api/sabores`

**Risco:** Com crescimento do banco, essas queries retornam toda a tabela sem LIMIT.

**Solução sugerida:**
```python
page  = max(1, request.args.get("page", 1, type=int))
limit = min(100, request.args.get("limit", 20, type=int))
offset = (page - 1) * limit
# SELECT ... LIMIT %s OFFSET %s
```

---

### ⚠️ Ponto frágil: Tokens JWT não podem ser revogados

**Onde:** `backend/auth/jwt_handler.py`

**Risco:** Token roubado permanece válido por até 24h sem possibilidade de invalidação.

**Solução sugerida:** Implementar tabela `revoked_tokens` (jti blacklist) ou usar `access_token` curto (15min) + `refresh_token` longo (7d) com endpoint `/api/auth/refresh`.

---

### ⚠️ Ponto frágil: Pedidos sem vínculo ao usuário

**Onde:** `database/schema.sql` — tabela `pedidos`

**Problema:** `pedidos` não tem `user_id`; impossível rastrear histórico de compras por cliente.

**Solução sugerida:**
```sql
ALTER TABLE pedidos ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
```

---

*Diagnóstico gerado automaticamente pelo Copilot Agent — branch `copilot/diagnostico-completo-projeto-atual`.*
