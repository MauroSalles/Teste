# 🍦 Gelateria Pro — Levantamento de PRs: Prisma Steve Jobs

> **Gerado em:** 2026-04-03 | **Branch de diagnóstico:** `copilot/sintetizar-status-pull-requests`  
> **Critérios de excelência:** Detalhe · Impacto · Inovação · Experiência

---

## Legenda de avaliação

| Símbolo | Significado |
|---------|-------------|
| ✅ | Pronto para merge — nível Apple |
| ⚠️ | Quase lá — falta o 1% que faz diferença |
| 🔄 | Conflito com `main` — precisa de rebase |
| 🚧 | WIP / Draft com lacunas estruturais |

**Nota Jobs (D·I·N·X):** Detalhe / Impacto / Inovação / Experiência — escala 1–5

---

## Sumário Executivo

| PR | Título (resumido) | Status | Conflito | Nota Jobs |
|----|-------------------|--------|----------|-----------|
| [#1](#pr-1) | v2.0 — Connection pooling, novos comandos, bug fix frontend | ✅ | ❌ | D:4 I:4 N:3 X:3 |
| [#13](#pr-13) | Pagamentos: Stripe, PIX, PayPal | 🚧 | ✅ | D:3 I:5 N:4 X:3 |
| [#14](#pr-14) | IA + ML: chatbot, recomendações, previsão | ✅ | ❌ | D:4 I:5 N:5 X:4 |
| [#15](#pr-15) | Notificações multicanal: email, SMS, push, WebSocket | 🚧 | ✅ | D:3 I:4 N:4 X:3 |
| [#17](#pr-17) | Loyalty: referral codes + coupon engine | ⚠️ | ✅ | D:3 I:4 N:3 X:3 |
| [#18](#pr-18) | Social commerce: Instagram, WhatsApp, AR | 🚧 | ✅ | D:3 I:4 N:5 X:3 |
| [#23](#pr-23) | Limpeza de repositório + README profissional | 🚧 | ✅ | D:2 I:3 N:2 X:2 |
| [#25](#pr-25) | Consolidação master (WebSocket, Pagamentos, IA, Loyalty) | 🚧 | ✅ | D:3 I:5 N:4 X:3 |
| [#26](#pr-26) | Landing page, /health/detailed, status page, Makefile | 🚧 | ✅ | D:3 I:4 N:3 X:3 |
| [#27](#pr-27) | Consolidação PR #25 + #26 | 🚧 | ✅ | D:3 I:5 N:4 X:3 |
| [#28](#pr-28) | v3.0 — APIs novas, páginas frontend, integrações | 🚧 | ✅ | D:3 I:4 N:4 X:3 |
| [#29](#pr-29) | v4.0 "Presence First" — Ritual diário, Feed, Auth, Viral | 🚧 | ✅ | D:3 I:5 N:5 X:4 |
| [#30](#pr-30) | Feedback API, Sabor do Dia, cardápio nutricional | 🚧 | ✅ | D:3 I:4 N:4 X:3 |
| [#31](#pr-31) | Diagnóstico + micro-inovações: /health/detailed, fade-in | ✅ | ❌ | D:4 I:3 N:3 X:4 |
| [#33](#pr-33) | Redis caching, nginx reverse proxy, /infra/healthz | ⚠️ | ✅ | D:4 I:5 N:4 X:4 |
| [#34](#pr-34) | v4.0 "Presence First" — Gelinho, Streak, Social Feed | ⚠️ | ✅ | D:4 I:5 N:5 X:5 |
| [#35](#pr-35) | Expansão modular: feature flags, i18n, API pública, franquias | ⚠️ | ✅ | D:4 I:5 N:5 X:4 |
| [#36](#pr-36) | Cache layer, analytics API, reviews, nginx, dashboard UX | 🔄 | ✅ | D:5 I:5 N:5 X:5 |
| [#37](#pr-37) | Inventário self-service de sabores com gestão de estoque | ⚠️ | ✅ | D:4 I:5 N:4 X:4 |

---

## Análise Detalhada por PR

---

### PR #1
**v2.0 — Connection pooling, novos comandos, frontend bug fix**  
Branch: `copilot/create-gelateria-management-system` | Estado: ✅ **Mergeable** | Não-draft

**O que entrega:**
- `ThreadedConnectionPool` psycopg2 em lugar de `connect()` por request
- 3 novos comandos no terminal CMD
- Correção do bug de histórico no frontend

**Nota Jobs:** D:4 I:4 N:3 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ **Sem testes** para os 3 novos comandos do terminal (apenas unit tests do serviço, não da rota HTTP)
- ❌ Nenhuma animação ou feedback visual ao executar novo comando — terminal parece estático
- ❌ Documentação dos novos comandos no `README.md` ausente
- ❌ Pool size hardcoded — deveria ser configurável via `DB_POOL_MIN` / `DB_POOL_MAX` env vars

**Micro-detalhes de acabamento:**
```
+ Adicionar `DB_POOL_MIN=2` e `DB_POOL_MAX=10` no .env.example com comentário explicativo
+ No terminal: typing indicator ("…") de 300ms antes de retornar resposta do cmd
+ README: tabela de comandos atualizada incluindo os 3 novos
```

---

### PR #13
**Pagamentos: Stripe, PIX (Braspag), PayPal + JWT auth**  
Branch: `copilot/add-payments-integration` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- Blueprint Flask para pagamentos multi-método
- Integração Stripe (cartão, Google Pay, Apple Pay)
- PIX dinâmico via Braspag
- PayPal
- JWT auth em endpoints de pagamento

**Nota Jobs:** D:3 I:5 N:4 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ **Webhooks** ausentes — Stripe/PayPal notificam por webhook, sem isso pagamentos ficam "pendentes" para sempre
- ❌ Sem **idempotency keys** — duplo clique pode gerar dois cobranças
- ❌ Sem teste de reembolso/chargeback
- ❌ PCI-DSS: logs não devem conter dados de cartão — não há sanitização de logs
- ❌ UI de pagamento ausente — a "mágica" só existe se o usuário ver o checkout fluir
- ❌ Conflito de merge com `main` (rebase necessário)

**Micro-detalhes de acabamento:**
```
+ Endpoint POST /api/pagamentos/webhook (Stripe + PayPal) com verificação de assinatura HMAC
+ Idempotency key via X-Idempotency-Key header ou UUID gerado no frontend
+ Checkout modal animado no frontend: "Pague com PIX 🔲" → mostra QR code com timer de 15min
+ Mascarar dados sensíveis no logger: truncar card_number, ocultar CVV
```

---

### PR #14
**IA + ML: chatbot, recomendações, previsão de demanda, churn, sentimento**  
Branch: `copilot/add-openai-chatbot-integration` | Estado: ✅ **Não-draft** | Mergeable

**O que entrega:**
- 6 módulos de serviço ML
- Blueprint Flask com 6 endpoints
- Widget de chat no frontend
- Suite de testes

**Nota Jobs:** D:4 I:5 N:5 X:4

**O que falta para o OK de Steve Jobs:**
- ❌ Chat widget sem **modo offline/fallback** gracioso — se OpenAI estiver fora, experiência quebra
- ❌ Recomendações não são **personalizadas por usuário logado** (sem session context)
- ❌ Sem **streaming** da resposta do chatbot — resposta aparece de uma vez, sem efeito "digitando"
- ❌ Testes de integração mock não cobrem falha da API OpenAI

**Micro-detalhes de acabamento:**
```
+ Streaming da resposta do GPT via Server-Sent Events (SSE): cada token aparece em tempo real
+ Fallback off-line: 30+ respostas curadas por categoria (mais barato e resiliente)
+ Histórico de conversa no localStorage (últimas 10 mensagens)
+ Widget: botão "Copiar resposta" + "Compartilhar sabor recomendado" via Web Share API
```

---

### PR #15
**Notificações multicanal: email (SMTP), SMS (Twilio), push, WebSocket, smart timing**  
Branch: `copilot/notifications-full-stack-communication-engine` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- Email service (SMTP/SendGrid)
- SMS via Twilio
- Push via Firebase Cloud Messaging
- WebSocket broadcast
- Smart timing engine

**Nota Jobs:** D:3 I:4 N:4 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ **Preferências do usuário** ausentes — usuário não pode escolher quais canais quer
- ❌ Sem **unsubscribe** no email — obrigatório pelo CAN-SPAM/LGPD
- ❌ Sem **template de email** visual — texto plano não converte
- ❌ WebSocket sem reconexão automática no frontend
- ❌ Sem testes do smart timing (apenas mock de envio)

**Micro-detalhes de acabamento:**
```
+ Tabela `notification_preferences` (user_id, channel, enabled) com endpoint PATCH /api/notifications/preferences
+ Template HTML de email com logo Gelateria + CTA colorido + "Cancelar inscrição" no rodapé
+ Frontend WebSocket: reconnect exponential backoff (1s → 2s → 4s → max 30s)
+ Respeitar horário de silêncio: smart timing não envia push entre 22h–8h
```

---

### PR #17
**Loyalty: referral codes + coupon engine protegido contra fraude**  
Branch: `copilot/add-referral-and-coupon-system` | Estado: ⚠️ Draft | Conflito com main

**O que entrega:**
- Programa de indicação com cupons em cascata
- Pipeline de validação de cupom resistente a fraude
- Adaptado ao padrão `get_db()` do projeto

**Nota Jobs:** D:3 I:4 N:3 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ **Sem UI** — o usuário não vê seu código de referral em lugar algum
- ❌ Sem **compartilhamento nativo** do código (Web Share API)
- ❌ Expiração de cupom hardcoded — não configurável
- ❌ Sem notificação quando uma indicação converte ("Seu amigo acabou de usar seu código! 🎉")
- ❌ Conflito de merge; código de cupom não se integra ao checkout do PR #13

**Micro-detalhes de acabamento:**
```
+ Seção "Indique e Ganhe" no dashboard: QR Code do link + botão "Compartilhar"
+ Notificação push/email quando indicação converte
+ Animação confete (canvas-confetti, ~3KB) ao primeiro resgate
+ Expiração configurável via COUPON_EXPIRY_DAYS env var
```

---

### PR #18
**Social commerce: Instagram Shopping, WhatsApp Business, AR preview**  
Branch: `copilot/add-instagram-shopping-integration` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- Blueprint Flask para canais sociais
- Instagram shoppable posts/lives
- WhatsApp ordering via Twilio
- AR product preview

**Nota Jobs:** D:3 I:4 N:5 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ Integração Instagram **requer aprovação do Meta** — sem nota sobre processo de revisão (bloqueia produção)
- ❌ WhatsApp sem **menu interativo** (List Message/Button Reply) — só texto plano é fraco
- ❌ AR preview sem **fallback 2D** para dispositivos sem suporte WebXR
- ❌ Sem tratamento de webhook de status de entrega de mensagem WhatsApp

**Micro-detalhes de acabamento:**
```
+ Documentar no README a jornada de aprovação Instagram API (1-4 semanas)
+ WhatsApp: List Message com sabores categorizados (Açaí / Sorvete / Especiais)
+ AR: detector de suporte WebXR com fallback para galeria 3D estática (Three.js viewer)
+ Mock mode: SOCIAL_MOCK=1 simula envios sem credenciais reais (essencial para CI)
```

---

### PR #23
**Limpeza de repositório + README profissional**  
Branch: `copilot/cleanup-repository-professional-readme` | Estado: 🚧 WIP Draft | Conflito com main

**O que entrega:**
- Reorganização do repositório
- README atualizado

**Nota Jobs:** D:2 I:3 N:2 X:2

**O que falta para o OK de Steve Jobs:**
- ❌ PR ainda **WIP** sem checklist de conclusão
- ❌ README não tem screenshots reais (apenas placeholders)
- ❌ Sem badges de CI/CD, cobertura de testes ou versão

**Micro-detalhes de acabamento:**
```
+ Badges: CI status, test coverage, deploy status, license
+ Screenshots reais da UI (terminal + dashboard + profile)
+ Seção "Roadmap" como tabela com status (✅/🚧/🔮)
+ "One-liner deploy": docker compose up -d com gif animado de onboarding
```

---

### PR #25
**Consolidação master — WebSocket, Pagamentos, IA, Loyalty, Notificações**  
Branch: `copilot/consolidacao-definitiva-gelateria` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- Eleva o projeto a SaaS profissional
- Consolida features dos PRs #13–#18

**Nota Jobs:** D:3 I:5 N:4 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ **Consolidação** sem garantia de compatibilidade com features de PRs posteriores
- ❌ Sem migration script para schema changes acumulados
- ❌ Nenhum plano de rollback documentado
- ❌ Duplicação de endpoints com `main` não resolvida

**Micro-detalhes de acabamento:**
```
+ Script de migration numerada: 001_consolidation.sql com rollback idempotente
+ Endpoint GET /api/version retornando commit SHA + timestamp de build
+ Health check que valida schema version vs. esperado pela aplicação
```

---

### PR #26
**Landing page, /health/detailed, status page, versão cmd, Makefile, .env.example**  
Branch: `copilot/cleanup-obsolete-prs` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- Landing page pública
- Status page de infra
- Makefile para dev experience
- .env.example completo

**Nota Jobs:** D:3 I:4 N:3 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ Landing page sem **above-the-fold** impactante — "primeiro segundo" da visita decide retenção
- ❌ Status page sem **histórico de uptime** (apenas estado atual)
- ❌ Makefile sem alvo `make help` que lista os comandos

**Micro-detalhes de acabamento:**
```
+ Landing: hero animado com sorvete flutuando (Lottie JSON, <50KB), CTA "Começar grátis" visível sem scroll
+ Status page: sparkline de uptime dos últimos 30 dias por componente
+ make help: gera tabela automática a partir de comentários ## acima de cada target
+ Open Graph meta tags na landing (título, descrição, imagem de compartilhamento)
```

---

### PR #27
**Consolidação PR #25 + #26 — Real-time, Payments, AI, Loyalty, Notifications & Landing**  
Branch: `copilot/merge-pr-25-26-into-main` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- Entrega do escopo completo de #25 e #26 em squash commits

**Nota Jobs:** D:3 I:5 N:4 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ Mesmo problema de #25: conflito acumulado com `main` não resolvido
- ❌ Squash de dois grandes features em um único PR dificulta revisão e rollback granular
- ❌ Sem demo/screenshots comparativos antes/depois

**Micro-detalhes de acabamento:**
```
+ Dividir em dois PRs pequenos sequenciais (infraestrutura first, features depois)
+ Screenshots comparativos: dashboard antes vs. depois do consolidado
+ Checklist de smoke tests pós-merge no corpo do PR
```

---

### PR #28
**v3.0 — 5 novos blueprints API, 5 páginas frontend, integrações**  
Branch: `copilot/add-new-backend-apis` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- 5 blueprints Flask novos
- 5 páginas frontend
- Integração terminal com APIs novas

**Nota Jobs:** D:3 I:4 N:4 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ 5 páginas sem **design system consistente** — cada uma tem estilo próprio
- ❌ Navegação entre páginas sem **loading state** — flash de conteúdo
- ❌ Nenhuma das novas pages é **PWA-aware** (sem service worker extension)

**Micro-detalhes de acabamento:**
```
+ Shared CSS tokens: --color-primary, --radius, --spacing padronizados em style.css
+ Page transition: fade 150ms via View Transitions API (Chrome 111+) com fallback opacity
+ Cache pages no service worker: stale-while-revalidate para páginas estáticas
```

---

### PR #29
**v4.0 "Presence First" — 26 endpoints, Daily Ritual, Clube, Feed Social, Auth**  
Branch: `copilot/add-sabor-do-dia-feature` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- 26 novos endpoints
- 5 novas tabelas DB
- Telas frontend para ritual diário, clube, feed

**Nota Jobs:** D:3 I:5 N:5 X:4

**O que falta para o OK de Steve Jobs:**
- ❌ 26 endpoints em um único PR é **review impossible** — ninguém lê com cuidado
- ❌ Streak sem **notificação de "quase perdendo"** — sem urgência = sem engajamento
- ❌ Clube de assinatura sem integração com sistema de pagamento do PR #13
- ❌ Feed social sem moderação/reporting de conteúdo inapropriado

**Micro-detalhes de acabamento:**
```
+ Push notification: "🍦 Seu streak de 7 dias está em risco! Faça check-in hoje"
+ Clube: mock de checkout com botão "Ativar plano" (conectar ao PR #13 quando mergeado)
+ Feed: botão "Reportar" em cada post (envia para tabela reports com email admin)
+ Calendário de contribuições: grid estilo GitHub mostrando check-ins dos últimos 52 semanas
```

---

### PR #30
**Feedback API, Sabor do Dia, cardápio nutricional, health check estendido, easter eggs**  
Branch: `copilot/transformar-website-gelateria` | Estado: 🚧 Draft | Conflito com main

**O que entrega:**
- POST/GET /api/feedback
- Sabor do Dia determinístico
- Tabela nutricional
- Easter eggs

**Nota Jobs:** D:3 I:4 N:4 X:3

**O que falta para o OK de Steve Jobs:**
- ❌ Feedback API sem **moderação** — qualquer texto vai direto para o banco
- ❌ Tabela nutricional com dados **fictícios** — erro de credibilidade se usuário perceber
- ❌ Easter eggs sem documentação da sequência de ativação (Konami code?)
- ❌ Sabor do Dia duplicado com PR #34 — risco de conflito semântico

**Micro-detalhes de acabamento:**
```
+ Feedback: validação de conteúdo (min 10, max 500 chars) + honeypot field anti-spam
+ Nutricional: marcar claramente como "valores aproximados" ou "tabela ilustrativa"
+ Easter egg: sequência ↑↑↓↓←→←→BA ativa "Modo Sorvete" (cursor vira 🍦, partículas de confete)
+ Consolidar Sabor do Dia com PR #34 antes de merge
```

---

### PR #31
**Diagnóstico + micro-inovações: /health/detailed, tab-completion, fade-in, typing dots**  
Branch: `copilot/diagnostico-regressoes-e-sugestoes` | Estado: ✅ **Não-draft** | Mergeable

**O que entrega:**
- `/health/detailed` com status DB, JWT, uptime
- Tab-completion no terminal
- Fade-in de resposta
- Typing dots (loading)
- Pulse de danger em alertas

**Nota Jobs:** D:4 I:3 N:3 X:4

**O que falta para o OK de Steve Jobs:**
- ❌ Tab-completion sem **preview inline** (modo "ghost text" como VS Code/Copilot)
- ❌ Typing dots sem **cancel button** — usuário preso esperando resposta lenta
- ❌ `/health/detailed` sem **timestamp da última checagem** — não dá para saber se está atualizado
- ❌ Pulse de danger não tem **som** opcional (acessibilidade: alerta visual sem som exclui usuários com deficiência visual)

**Micro-detalhes de acabamento:**
```
+ Tab-completion: ghost text cinza após cursor (ex: "listar sab|ores") ao pressionar →
+ Typing dots: botão ✕ cancela request em flight via AbortController
+ /health/detailed: campo "checked_at" ISO 8601 na resposta JSON
+ Pulse: aria-live="assertive" no elemento de alerta (acessibilidade sem som)
```

---

### PR #33
**Redis caching layer, nginx reverse proxy, /infra/healthz endpoint**  
Branch: `copilot/merge-all-optimization-proxy` | Estado: ⚠️ Draft | Conflito com main

**O que entrega:**
- Cache Redis com fallback em memória
- nginx como API gateway com rate limiting
- `/infra/healthz` cobrindo todos os componentes de infra

**Nota Jobs:** D:4 I:5 N:4 X:4

**O que falta para o OK de Steve Jobs:**
- ❌ nginx config sem **HTTP/2** habilitado (h2 reduz 30-40% latência em múltiplos assets)
- ❌ Redis sem **eviction policy** definida — memória pode encher silenciosamente
- ❌ Cache invalidation sem **granularidade** — `flush_all` invalida tudo junto
- ❌ `/infra/healthz` sem **SLA** documentado (qual o threshold de "degradado" vs "offline"?)

**Micro-detalhes de acabamento:**
```nginx
# nginx.conf
http2 on;  # habilitar HTTP/2

# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
```
```python
# cache.py: invalidação granular por tag
cache.delete_pattern("sabores:*")   # invalida apenas endpoints de sabores
```
```
+ /infra/healthz: campo "sla_ms" por componente (ex: db < 100ms = healthy, < 500ms = degraded)
```

---

### PR #34
**v4.0 "Presence First" — Gelinho mascote, Sabor do Dia, Streak, Social Feed, Perfil**  
Branch: `copilot/optimizacoes-gerais-produto` | Estado: ⚠️ Draft | Conflito com main

**O que entrega:**
- Gelinho 🍦 mascote com idle timer de 30s
- Sabor do Dia determinístico (sem DB)
- Check-in com streak e mood
- Social feed com likes
- Página de perfil pública com QR
- Dashboard redesenhado (purple/gradient)

**Screenshots incluídos:** ✅ Dashboard, Terminal, Profile

**Nota Jobs:** D:4 I:5 N:5 X:5

**O que falta para o OK de Steve Jobs:**
- ❌ Gelinho responde com frases genéricas — sem **personalização por horário/sabor do dia**
- ❌ Streak quebrado **não tem recuperação** (grace period de 12h seria mais humano)
- ❌ Social feed sem **lazy loading** de imagens nem paginação — vai travar com volume
- ❌ Profile QR aponta para URL sem validação de `https://` em produção
- ❌ Dashboard novo não tem **modo dark consistente** (tokens do CSS antigo colidem)

**Micro-detalhes de acabamento:**
```
+ Gelinho: contexto dinâmico → manhã "Bom dia! ☀️ O sabor de hoje é {sabor_do_dia}"
+ Streak grace period: 28h (não 24h) → usuário mantém streak se checar com até 4h de atraso
+ Feed: Intersection Observer para lazy load + cursor-based pagination (cursor=último_id)
+ Profile QR: HTTPS enforcement via window.location.protocol check + canonical URL
+ CSS: auditar variáveis --color-*, extrair paleta roxa em nova seção do style.css
```

---

### PR #35
**Expansão modular: feature flags, i18n, API pública, franquias, multi-tenant, OpenAPI**  
Branch: `copilot/inicio-planejamento-expansao-modular` | Estado: ⚠️ Draft | Conflito com main

**O que entrega:**
- Feature flags via env vars (`FEATURE_*=1`)
- i18n para pt/en/es via Accept-Language
- API key auth (`@api_key_required`)
- Módulo de parceiros e franquias
- Multi-tenant via env vars
- OpenAPI 3.0 spec em `/api/docs`
- Onboarding guiado em `/api/onboarding`

**Nota Jobs:** D:4 I:5 N:5 X:4

**O que falta para o OK de Steve Jobs:**
- ❌ Feature flags via env vars **não permitem hot reload** — requer restart para ativar
- ❌ OpenAPI spec gerado manualmente — vai ficar desatualizado (usar `flask-smorest` ou `flasgger` para auto-gen)
- ❌ i18n sem **persistência de preferência** (cookie/localStorage) — muda a cada request se Accept-Language variar
- ❌ Franquia com status `pending → active` sem **email de notificação** ao admin
- ❌ Onboarding sem checklist de conclusão visual

**Micro-detalhes de acabamento:**
```
+ Feature flags: tabela `feature_flag_overrides` no DB para hot-toggle sem restart
+ OpenAPI: migrar para flask-smorest (auto-gera spec a partir de decorators)
+ i18n: cookie `gelateria_lang` com max-age=1year sobrescreve Accept-Language
+ Franquia aprovada: email ao solicitante com link de dashboard e próximos passos
+ Onboarding: barra de progresso (steps 1/5) com animação de confete ao completar
```

---

### PR #36
**Cache layer, analytics API, reviews, nginx proxy, dashboard UX overhaul**  
Branch: `copilot/run-parallel-improvement-process` | Estado: 🔄 **Conflito (dirty)** | Draft

**O que entrega:**
- `backend/cache.py`: TTL cache thread-safe com fallback Redis
- `/api/analytics/*`: overview, tendência, ranking, alertas, cache info
- Sistema de reviews: GET/POST por sabor, ranking
- Middleware `X-Request-ID` para correlation logging
- Liveness `/health/live` + Readiness `/health/ready`
- Dashboard: contadores animados, toasts, skeleton loading, atalho `R`
- nginx: gzip, headers de segurança, rate limiting, cache de assets 7d

**Nota Jobs:** D:5 I:5 N:5 X:5

**O que falta para o OK de Steve Jobs:**
- ❌ **Conflito de merge** com `main` — impede qualquer merge imediato
- ❌ Analytics sem **filtro de período** na UI (apenas backend suporta)
- ❌ Reviews sem **resposta do proprietário** (o dono da gelateria não pode responder avaliações)
- ❌ Rate limiting nginx não tem **whitelist** para IPs internos/CI
- ❌ Dashboard skeleton loading sem **aria-busy="true"** — leitores de tela não percebem

**Micro-detalhes de acabamento:**
```
+ Analytics UI: DateRangePicker nativo (<input type="date">) filtrado via ?de=&ate= params
+ Reviews: campo `owner_reply` na tabela + endpoint PATCH /api/reviews/{id}/reply (JWT admin)
+ nginx: $http_x_forwarded_for whitelist para 127.0.0.1/::1 sem rate limit
+ Skeleton: aria-busy="true" → aria-busy="false" ao carregar dados
+ Resolver conflito de merge: git rebase origin/main --autostash
```

---

### PR #37
**Inventário self-service de sabores com endpoints de gestão de estoque**  
Branch: `copilot/add-estoque-sabores-import` | Estado: ⚠️ Draft | Conflito com main

**O que entrega:**
- Tabela `estoque_sabores` com 36 sabores pré-cadastrados (açaí + sorvete)
- Mínimos de estoque para 5 sabores de alto giro
- Endpoints: GET /api/estoque/faltando, POST /api/estoque/pedido-semanal, POST /api/estoque/atualizar
- Frontend `estoque.html` com 4 abas e auto-refresh 60s

**Nota Jobs:** D:4 I:5 N:4 X:4

**O que falta para o OK de Steve Jobs:**
- ❌ Estoque mínimo **estático** — não aprende com padrão de vendas
- ❌ Pedido semanal sem **exportação PDF** para o fornecedor
- ❌ `estoque.html` sem **ordenação** por coluna clicável na tabela
- ❌ Auto-refresh de 60s sem **indicador visual** de quando o próximo refresh ocorre
- ❌ Sem **histórico** de variação de estoque (saber que determinado dia esgotou um sabor)

**Micro-detalhes de acabamento:**
```
+ Estoque mínimo dinâmico: cron job semanal que ajusta mínimo = média das últimas 4 semanas × 1.2
+ Exportar pedido: botão "📄 Gerar PDF do Pedido" usando window.print() com @media print estilizado
+ Tabela: <th> clicável com ícone ↑↓ para sort JS client-side (sem request adicional)
+ Countdown visual: barra de progresso slim no topo pulsando nos últimos 10s antes do refresh
+ Tabela `estoque_historico`: snapshot diário de quantidade_atual via cron/trigger
```

---

## 🏆 Ranking de Prioridade — Ordem de Merge Sugerida

> Baseado em: impacto imediato + menor risco de conflito + menor breaking change

| Ordem | PR | Motivo |
|-------|----|--------|
| 1️⃣ | **#31** | Mergeable, não-draft, qualidade boa, impacto UX imediato |
| 2️⃣ | **#1** | Mergeable, não-draft, base técnica sólida |
| 3️⃣ | **#14** | Mergeable, não-draft, diferencial competitivo forte |
| 4️⃣ | **#36** | Maior impacto técnico — resolver conflito e mergear (infraestrutura + analytics + cache) |
| 5️⃣ | **#34** | Melhor experiência produto — resolver conflito e mergear (Presence First + mascote) |
| 6️⃣ | **#37** | Dados reais do negócio — resolver conflito e mergear (inventário + estoque) |
| 7️⃣ | **#33** | Redis + nginx para produção — resolver conflito e mergear |
| 8️⃣ | **#35** | Expansão modular — feature flags + i18n (fundação para tudo mais) |
| 9️⃣ | **#17** | Loyalty com referral — engajamento viral |
| 🔟 | **#13** | Pagamentos — receita real (depende de webhook impl. primeiro) |

> PRs #25, #26, #27, #28, #29, #30 têm sobreposição com os acima — avaliar o que é único em cada um antes de mergear para evitar duplicação.

---

## 🔑 Os 5 Micro-detalhes que Steve Jobs Exigiria Imediatamente

1. **Carregamento instantâneo** — skeleton screens em cada lista (PR #36 já tem; estender para todas as páginas)
2. **Feedback háptico/sonoro ao completar ação** — um "ding" suave (AudioContext, <1KB) quando pedido é criado ou ponto ganho
3. **Zero estado em branco** — toda tabela/lista vazia mostra ilustração + CTA ("Adicionar primeiro sabor ✨")
4. **Nome do usuário em todo lugar** — navbar deve mostrar "Olá, Mauro 👋" logo após login (PR #34 tem streak badge mas não nome)
5. **Share nativo em cada conquista** — badge desbloqueada, streak novo, review positiva → Web Share API com imagem OG gerada no servidor

---

## 🚨 Débitos Técnicos Críticos (presentes em múltiplos PRs)

| Problema | PRs afetados | Solução express |
|----------|-------------|-----------------|
| **Sem rate limiting em auth** | Main, #25, #27, #33 | `Flask-Limiter` 10/min em `/api/auth/login` |
| **innerHTML XSS** | Main, #34 | Substituir por `textContent` ou DOMPurify |
| **Tokens JWT sem revogação** | Main, #25, #27 | Short-lived access (15min) + refresh token |
| **Sem paginação nas listagens** | Main, #28, #29 | `?page=1&limit=20` em todos os GETs de lista |
| **Conflitos de merge acumulados** | #13, #15, #17, #18, #23, #25–#30, #33–#37 | Rebase sequencial na ordem da tabela acima |

---

*Diagnóstico gerado pela branch `copilot/sintetizar-status-pull-requests` — PR #38*  
*Para mergear qualquer PR com conflito: `git checkout <branch> && git rebase origin/main`*
