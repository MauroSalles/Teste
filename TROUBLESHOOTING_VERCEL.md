# 🔧 TROUBLESHOOTING VERCEL — Por que o Vercel não vincula com o GitHub?

> Este guia explica por que o Vercel pode falhar ao conectar com sua conta GitHub e como resolver.

---

## Índice

1. [Por que o Vercel não vincula com o GitHub](#1-por-que-o-vercel-não-vincula-com-o-github)
2. [Solução 1 — Re-autorizar o OAuth do Vercel](#2-solução-1--re-autorizar-o-oauth-do-vercel)
3. [Solução 2 — Usar Personal Access Token (PAT)](#3-solução-2--usar-personal-access-token-pat)
4. [Solução 3 — Deploy manual via Vercel CLI](#4-solução-3--deploy-manual-via-vercel-cli)
5. [Alternativa — Usar Netlify](#5-alternativa--usar-netlify)
6. [Perguntas Frequentes](#6-perguntas-frequentes)

---

## 1. Por que o Vercel não vincula com o GitHub

### Causas mais comuns

| Causa | Sintoma |
|-------|---------|
| Aplicação OAuth não autorizada na conta GitHub | "Error: OAuth app access restriction" |
| Token OAuth expirado ou revogado | Volta à tela de login repetidamente |
| Restrições de organização GitHub | "Organization not accessible" |
| Conta GitHub usa autenticação 2FA mas Vercel não a suporta corretamente | Loop de autorização |
| Cookies/cache do navegador corrompidos | Página de autorização em branco ou congelada |

### O que acontece por trás dos panos

1. Quando você clica em **"Continue with GitHub"** no Vercel, ele redireciona para o GitHub OAuth.
2. O GitHub pede permissão para o Vercel acessar seus repositórios.
3. Se a organização ou conta tiver restrições de OAuth, o GitHub bloqueia o acesso.
4. O Vercel não consegue listar seus repositórios.

---

## 2. Solução 1 — Re-autorizar o OAuth do Vercel

### Passo 1: Revogar a autorização antiga no GitHub

1. Acesse: https://github.com/settings/applications
2. Clique na aba **"Authorized OAuth Apps"**
3. Encontre **"Vercel"** na lista
4. Clique em **"Revoke"** → confirme

### Passo 2: Limpar cookies do navegador

1. Abra as configurações do navegador
2. Vá em **Privacidade → Limpar dados de navegação**
3. Marque **Cookies** e **Cache**
4. Clique em **Limpar dados**

### Passo 3: Re-autorizar

1. Acesse https://vercel.com/login
2. Clique em **"Continue with GitHub"**
3. Autorize o Vercel quando o GitHub pedir
4. Na tela de importação, selecione seu repositório `Teste`

---

## 3. Solução 2 — Usar Personal Access Token (PAT)

Se o OAuth continuar falhando, use um token pessoal do GitHub.

### Criar o PAT no GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em **"Generate new token (classic)"**
3. Dê um nome: `vercel-deploy`
4. Selecione as permissões:
   - ✅ `repo` (acesso total a repositórios)
   - ✅ `workflow` (se usar GitHub Actions)
5. Clique em **"Generate token"**
6. **Copie o token** — ele só aparece uma vez!

### Conectar o PAT ao Vercel

1. Na dashboard do Vercel, vá em **Settings → Git**
2. Clique em **"Connect with GitHub Token"**
3. Cole o token gerado
4. Clique em **"Connect"**

---

## 4. Solução 3 — Deploy manual via Vercel CLI

Se a interface web não funcionar, use a linha de comando.

### Instalar a Vercel CLI

```bash
npm install -g vercel
```

### Fazer login

```bash
vercel login
# Escolha "Continue with GitHub" e siga as instruções no navegador
# OU
vercel login --token SEU_TOKEN_AQUI
```

### Fazer deploy

```bash
# Na pasta raiz do projeto
cd Teste

# Primeiro deploy (faz perguntas de configuração)
vercel

# Deploy em produção
vercel --prod
```

### Configurar projeto via CLI

```bash
# Linkar projeto existente
vercel link

# Definir variáveis de ambiente
vercel env add NOME_DA_VARIAVEL

# Ver URL do deploy
vercel ls
```

---

## 5. Alternativa — Usar Netlify

O Netlify é uma excelente alternativa ao Vercel para hospedar o frontend.

### Por que Netlify?

- ✅ Integração com GitHub mais simples
- ✅ Subdomínio grátis: `seu-projeto.netlify.app`
- ✅ HTTPS automático
- ✅ Deploy automático a cada push
- ✅ Suporte a formulários, funções serverless

### Passo a passo no Netlify

#### 1. Criar conta

1. Acesse https://www.netlify.com
2. Clique em **"Sign up"**
3. Escolha **"Sign up with GitHub"**
4. Autorize o Netlify no GitHub

#### 2. Importar repositório

1. No dashboard do Netlify, clique em **"Add new site"**
2. Escolha **"Import an existing project"**
3. Clique em **"Deploy with GitHub"**
4. Selecione o repositório `MauroSalles/Teste`

#### 3. Configurar o build

| Campo | Valor |
|-------|-------|
| Base directory | `frontend` (se houver pasta frontend) |
| Build command | `npm run build` |
| Publish directory | `frontend/build` ou `frontend/dist` |

#### 4. Definir variáveis de ambiente

1. Vá em **Site settings → Environment variables**
2. Adicione:
   - `REACT_APP_API_URL` = URL do seu backend no Render

#### 5. Deploy

Clique em **"Deploy site"** — aguarde 1-2 minutos.

Sua URL será: `https://nome-aleatorio.netlify.app`

Para personalizar: vá em **Site settings → Domain management → Custom domains**.

---

## 6. Perguntas Frequentes

### "Organization not accessible" no Vercel

Sua organização GitHub pode ter restrições de acesso OAuth.

**Solução:**
1. Acesse: https://github.com/organizations/NOME_ORG/settings/oauth_application_policy
2. Procure "Vercel" na lista de apps
3. Clique em **"Grant"** para permitir o acesso

---

### O Vercel importa o repositório mas o deploy falha

Verifique os logs de build:
1. Vá no projeto no Vercel
2. Clique em **"Deployments"**
3. Clique no deploy com falha
4. Veja os logs em **"Build Logs"**

Erros comuns:
- `npm run build` falha → verifique o `package.json`
- Variável de ambiente ausente → adicione em **Settings → Environment Variables**

---

### O frontend no Vercel não consegue falar com o backend no Render

Verifique:
1. A URL do backend no Render está correta na variável de ambiente do Vercel
2. O CORS no backend permite a origem do Vercel:
   ```env
   ALLOWED_ORIGINS=https://seu-projeto.vercel.app
   ```
3. O backend no Render está rodando (o free tier "dorme" após inatividade — aguarde 30 segundos)

---

### Links úteis

- Documentação Vercel: https://vercel.com/docs
- Documentação Netlify: https://docs.netlify.com
- GitHub OAuth Apps: https://github.com/settings/applications
- GitHub Personal Tokens: https://github.com/settings/tokens
- Status do Vercel: https://www.vercel-status.com
- Status do Netlify: https://www.netlifystatus.com
