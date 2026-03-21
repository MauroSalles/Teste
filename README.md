# 🍦 Gelateria Sistema

Sistema de gestão para gelateria com interface tipo CMD web.  
**Backend:** Python + Flask | **Banco:** PostgreSQL | **Frontend:** HTML + CSS + JS

---

## 📁 Estrutura do Projeto

```
gelateria-system/
├── backend/
│   ├── app.py              ← Ponto de entrada Flask
│   ├── database.py         ← Conexão com PostgreSQL
│   ├── routes/
│   │   ├── cmd_routes.py   ← Rota /cmd
│   │   └── health_routes.py← Rota /health
│   ├── models/
│   │   ├── sabor.py        ← Operações na tabela sabores
│   │   └── pedido.py       ← Operações na tabela pedidos
│   └── services/
│       └── cmd_service.py  ← Lógica dos comandos
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── database/
│   └── schema.sql          ← Schema PostgreSQL
├── .github/workflows/
│   └── deploy.yml          ← CI/CD GitHub Actions
├── Dockerfile
├── docker-compose.yml
├── render.yaml             ← Config Render.com
├── vercel.json             ← Config Vercel
├── requirements.txt
└── .env.example
```

---

## 🚀 Rodando Localmente

### Pré-requisitos
- Python 3.12+
- PostgreSQL 14+
- Docker (opcional)

### 1. Clone e configure

```bash
git clone https://github.com/MauroSalles/Teste.git
cd Teste
cp .env.example .env
# Edite .env com suas credenciais do banco
```

### 2. Instale as dependências Python

```bash
pip install -r requirements.txt
```

### 3. Crie o banco de dados

```bash
psql -U postgres -c "CREATE DATABASE gelateria;"
psql -U postgres -d gelateria -f database/schema.sql
```

### 4. Inicie o backend

```bash
python -m backend.app
# Ou em modo desenvolvimento:
FLASK_ENV=development python -m backend.app
```

### 5. Abra o frontend

Abra `frontend/index.html` com a extensão **Live Server** do VS Code ou qualquer servidor HTTP.

---

## 🐳 Rodando com Docker Compose

```bash
cp .env.example .env
# Edite DB_PASSWORD no .env
docker-compose up --build
```

| Serviço   | URL                    |
|-----------|------------------------|
| Frontend  | http://localhost:3000  |
| Backend   | http://localhost:5000  |
| Banco     | localhost:5432         |

---

## 💻 Comandos do Sistema

| Comando                          | Descrição                      |
|----------------------------------|--------------------------------|
| `ajuda`                          | Lista todos os comandos        |
| `listar sabores`                 | Mostra sabores cadastrados     |
| `add sabor <nome> <preco>`       | Adiciona um novo sabor         |
| `remover sabor <id>`             | Remove um sabor pelo ID        |
| `fazer pedido <sabor> <qtd>`     | Registra um pedido             |
| `listar pedidos`                 | Mostra histórico de pedidos    |

### Exemplos

```
❯ listar sabores
  ID: 1 | Chocolate - R$ 10.00
  ID: 2 | Morango - R$ 9.50

❯ add sabor Pistache 12.00
  Sabor 'Pistache' adicionado com sucesso!

❯ fazer pedido Chocolate 3
  Pedido registrado: 3x Chocolate — R$ 30.00
```

---

## ☁️ Deploy em Produção

### Backend → Render.com

1. Crie conta em [render.com](https://render.com)
2. Clique em **New → Blueprint** e aponte para este repositório
3. O arquivo `render.yaml` configura automaticamente:
   - Web service com Docker
   - Banco de dados PostgreSQL gerenciado
   - Health check em `/health`
4. Configure a variável `ALLOWED_ORIGINS` no painel do Render com a URL do seu frontend

### Frontend → Vercel

1. Crie conta em [vercel.com](https://vercel.com)
2. Importe este repositório
3. Configure:
   - **Root Directory:** `frontend`
   - **Environment Variable:** `API_URL` = URL do seu backend no Render
4. Clique em **Deploy**

### CI/CD — GitHub Actions

Configure estes secrets no repositório (`Settings → Secrets → Actions`):

| Secret                    | Descrição                                          |
|---------------------------|----------------------------------------------------|
| `RENDER_DEPLOY_HOOK_URL`  | URL do deploy hook do Render (Settings do serviço) |
| `VERCEL_TOKEN`            | Token de API do Vercel (`vercel.com/account/tokens`)|
| `VERCEL_ORG_ID`           | ID da sua organização no Vercel                    |
| `VERCEL_PROJECT_ID`       | ID do projeto no Vercel                            |

A cada `git push` para `main`:
- ✅ Testes rodam automaticamente
- ✅ Imagem Docker é construída e validada
- ✅ Backend é deployado no Render
- ✅ Frontend é deployado no Vercel

### Domínio .com

1. Compre um domínio em [Namecheap](https://namecheap.com) ou [GoDaddy](https://godaddy.com)
2. No Vercel: `Project Settings → Domains → Add Domain`
3. No Render: `Service Settings → Custom Domain → Add Domain`
4. Aponte os DNS conforme instruído pela plataforma — SSL/TLS é configurado automaticamente

---

## 🔐 Variáveis de Ambiente

| Variável          | Descrição                                  | Padrão        |
|-------------------|--------------------------------------------|---------------|
| `DATABASE_URL`    | URL completa do banco (Render/Railway)     | —             |
| `DB_HOST`         | Host do PostgreSQL (desenvolvimento local) | `localhost`   |
| `DB_NAME`         | Nome do banco de dados                     | `gelateria`   |
| `DB_USER`         | Usuário do banco                           | `postgres`    |
| `DB_PASSWORD`     | Senha do banco                             | —             |
| `DB_PORT`         | Porta do banco                             | `5432`        |
| `PORT`            | Porta do servidor Flask/Gunicorn           | `5000`        |
| `FLASK_ENV`       | Ambiente (`development`/`production`)      | `production`  |
| `ALLOWED_ORIGINS` | Origins permitidas para CORS               | `*`           |

---

## 🛠️ Tecnologias

- **Backend:** Python 3.12, Flask 3, Gunicorn
- **Banco:** PostgreSQL 16
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Container:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Hospedagem:** Render (backend), Vercel (frontend)
