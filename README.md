# 🍦 Gelateria Sistema

Sistema profissional de gerenciamento de gelateria com interface tipo **CMD Web**.

## Funcionalidades

| Comando | Descrição |
|---|---|
| `ajuda` | Exibe todos os comandos disponíveis |
| `limpar` / `cls` | Limpa a tela do terminal |
| `listar sabores` | Lista sabores cadastrados com ID e preço |
| `buscar sabor <termo>` | Busca sabores pelo nome (parcial) |
| `add sabor <nome> <preço>` | Adiciona um novo sabor |
| `remover sabor <id>` | Remove sabor pelo ID |
| `listar pedidos` | Lista todos os pedidos |
| `fazer pedido <cliente> <sabor> <qtd>` | Cria um novo pedido |
| `cancelar pedido <id>` | Cancela pedido e restaura estoque |
| `listar clientes` | Lista clientes com total de pedidos |
| `listar estoque` | Mostra estoque atual |
| `atualizar estoque <sabor> <qtd>` | Atualiza quantidade no estoque |

---

## Estrutura do Projeto

```
gelateria-system/
├── backend/
│   ├── app.py              # Entry-point Flask
│   ├── database.py         # Connection pool (psycopg2 ThreadedConnectionPool)
│   ├── requirements.txt
│   ├── routes/
│   │   ├── __init__.py
│   │   └── cmd_routes.py   # Endpoint /cmd
│   ├── models/
│   │   └── __init__.py     # Dataclasses de domínio
│   └── services/
│       ├── __init__.py
│       ├── sabores_service.py
│       ├── pedidos_service.py
│       ├── estoque_service.py
│       └── clientes_service.py
├── frontend/
│   ├── index.html          # Interface CMD Web
│   ├── style.css           # Terminal dark theme + spinner
│   └── script.js           # Fetch API + histórico + limpar
├── database/
│   └── schema.sql          # Tabelas PostgreSQL (constraints + índices)
└── README.md
```

---

## Tecnologias

- **Frontend:** HTML5, CSS3, Vanilla JS
- **Backend:** Python 3.9+, Flask, Flask-CORS
- **Database:** PostgreSQL
- **Deploy:** Render / Railway / Vercel

---

## Como Rodar Localmente

### 1. Pré-requisitos

- Python 3.9+
- PostgreSQL
- Git

### 2. Banco de Dados

```bash
psql -U postgres -f database/schema.sql
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt

# Crie o arquivo .env com as credenciais do banco
cp .env.example .env
# Edite .env com suas configurações

python app.py
```

### 4. Frontend

Abra `frontend/index.html` diretamente no navegador ou use a extensão **Live Server** do VS Code.

---

## Variáveis de Ambiente (`.env`)

```env
DB_HOST=localhost
DB_NAME=gelateria
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_PORT=5432
FLASK_ENV=development
```

---

## Deploy

### Backend — Render / Railway

1. Suba o código no GitHub
2. Crie um novo serviço Web no Render/Railway
3. Defina o **Build Command:** `pip install -r requirements.txt`
4. Defina o **Start Command:** `gunicorn app:app`
5. Configure as variáveis de ambiente

### Frontend — Vercel / Netlify

1. Aponte para a pasta `frontend/`
2. Defina a variável `API_URL` com a URL do backend em produção

> **Dica:** Edite a primeira linha de `frontend/script.js` ou defina `window.API_URL` antes de carregar o script para apontar para o backend em produção.

---

## Licença

MIT
