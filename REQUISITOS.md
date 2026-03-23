# 📋 REQUISITOS — O que instalar antes de começar

> Siga esta lista de cima para baixo antes de rodar qualquer script.  
> Use ☐ para marcar cada item conforme concluí-lo.

---

## 1. Software Obrigatório

| ☐ | Programa | Versão mínima | Tamanho aprox. | Link de download |
|---|----------|--------------|----------------|-----------------|
| ☐ | **Git** | 2.x | ~50 MB | https://git-scm.com/downloads |
| ☐ | **Python** | 3.9+ | ~30 MB | https://www.python.org/downloads/ |
| ☐ | **Node.js** | 16+ | ~70 MB | https://nodejs.org/en/download |
| ☐ | **PostgreSQL** | 12+ | ~300 MB | https://www.postgresql.org/download/ |
| ☐ | **Visual Studio Code** | qualquer | ~100 MB | https://code.visualstudio.com/Download |

### Docker (opcional, mas recomendado)

| ☐ | Programa | Link |
|---|----------|------|
| ☐ | **Docker Desktop** | https://www.docker.com/products/docker-desktop/ |

---

## 2. Como verificar se cada programa está instalado

Abra o **Terminal** (macOS/Linux) ou **CMD/PowerShell** (Windows) e execute:

```bash
# Git
git --version
# Esperado: git version 2.x.x

# Python
python --version        # Windows
python3 --version       # macOS/Linux
# Esperado: Python 3.9.x ou superior

# pip (gerenciador de pacotes Python)
pip --version           # Windows
pip3 --version          # macOS/Linux
# Esperado: pip 22.x ou superior

# Node.js
node --version
# Esperado: v16.x.x ou superior

# npm
npm --version
# Esperado: 8.x.x ou superior

# PostgreSQL
psql --version
# Esperado: psql (PostgreSQL) 12.x ou superior

# Docker (opcional)
docker --version
# Esperado: Docker version 24.x.x ou superior
```

---

## 3. Extensões recomendadas do VS Code

Instale pelo menu **Extensions** (`Ctrl+Shift+X` / `Cmd+Shift+X`) ou clique nos links abaixo:

| ☐ | Extensão | Para quê serve |
|---|----------|---------------|
| ☐ | [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Suporte completo a Python |
| ☐ | [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) | IntelliSense avançado |
| ☐ | [ES7+ React/Redux Snippets](https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets) | Snippets para React/JS |
| ☐ | [Thunder Client](https://marketplace.visualstudio.com/items?itemName=rangav.vscode-thunder-client) | Testar API (similar ao Postman) |
| ☐ | [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) | Gerenciar containers |
| ☐ | [GitHub Copilot](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) | Assistente de IA |
| ☐ | [GitLens](https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens) | Histórico Git no editor |
| ☐ | [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) | Formatação de código |

---

## 4. Frameworks e bibliotecas Python (instalados via script)

O script `setup.sh` / `setup.bat` instala tudo automaticamente a partir do `requirements.txt`:

| Pacote | Versão | Para quê serve |
|--------|--------|---------------|
| Flask | 3.0.3 | Framework web (backend) |
| Flask-CORS | 4.0.0 | Permitir requisições cross-origin |
| psycopg2-binary | 2.9.9 | Conexão com PostgreSQL |
| python-dotenv | 1.0.1 | Carregar variáveis do `.env` |
| gunicorn | 22.0.0 | Servidor WSGI para produção |
| pytest | 8.1.1 | Testes automatizados |
| SQLAlchemy | 2.0.29 | ORM para banco de dados |
| alembic | 1.13.1 | Migrations do banco |

---

## 5. Troubleshooting — problemas comuns de instalação

### Python não é reconhecido no Windows
```
'python' is not recognized as an internal or external command
```
**Solução:** Marque a opção **"Add Python to PATH"** durante a instalação.  
Ou adicione manualmente: `C:\Users\SeuNome\AppData\Local\Programs\Python\Python3x\` ao PATH.

---

### pip não encontrado
```
pip: command not found
```
**Solução:**
```bash
python -m ensurepip --upgrade   # Windows
python3 -m ensurepip --upgrade  # macOS/Linux
```

---

### PostgreSQL não inicia / porta 5432 em uso
```
Error: could not connect to server: Connection refused
```
**Solução:**
```bash
# macOS (Homebrew)
brew services restart postgresql

# Linux
sudo systemctl restart postgresql

# Windows — abrir Services (services.msc) e reiniciar "postgresql-x64-xx"
```

---

### Permissão negada ao executar setup.sh (macOS/Linux)
```
permission denied: ./setup.sh
```
**Solução:**
```bash
chmod +x setup.sh
./setup.sh
```

---

### Node.js versão antiga
```
error: Node.js version X is not supported
```
**Solução:** Baixe a versão LTS mais recente em https://nodejs.org ou use o [nvm](https://github.com/nvm-sh/nvm):
```bash
nvm install 18
nvm use 18
```
