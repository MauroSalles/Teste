# 📋 Pré-requisitos — Gelateria Sistema

## ✅ Checklist de Instalação

### 1. Git
- **Download**: https://git-scm.com/downloads
- **Verificar**: `git --version`
- **Mínimo**: Git 2.30+

### 2. Python 3.9+
- **Download**: https://python.org/downloads
- **Verificar**: `python3 --version`
- **Mínimo**: Python 3.9 (recomendado: 3.12)
- ⚠️ **Windows**: marque "Add Python to PATH" durante a instalação

### 3. PostgreSQL 14+
- **Download**: https://postgresql.org/download
- **Verificar**: `psql --version`
- **Alternativa**: Use Docker (ver abaixo)

### 4. VS Code (recomendado)
- **Download**: https://code.visualstudio.com

#### Extensões recomendadas:
| Extensão | ID | Para quê |
|---|---|---|
| Python | `ms-python.python` | Intellisense + debug |
| Pylance | `ms-python.vscode-pylance` | Type checking |
| PostgreSQL | `ckolkman.vscode-postgres` | DB browser |
| REST Client | `humao.rest-client` | Testar API |
| GitLens | `eamodio.gitlens` | Git avançado |
| Prettier | `esbenp.prettier-vscode` | Format JS/HTML/CSS |

### 5. Docker (opcional, mas recomendado)
- **Download**: https://docker.com/get-started
- **Verificar**: `docker --version` e `docker compose version`
- Permite rodar PostgreSQL sem instalar localmente

### 6. Node.js 18+ (opcional)
- Necessário apenas para ferramentas de frontend avançadas
- **Download**: https://nodejs.org
- **Verificar**: `node --version`

---

## 🔍 Verificação Rápida

Execute este script para verificar tudo de uma vez:

```bash
# Linux/macOS
echo "Git: $(git --version)"
echo "Python: $(python3 --version)"
echo "pip: $(pip3 --version)"
echo "psql: $(psql --version 2>/dev/null || echo 'não instalado')"
echo "Docker: $(docker --version 2>/dev/null || echo 'não instalado')"
```

```powershell
# Windows (PowerShell)
"Git: $(git --version)"
"Python: $(python --version)"
"psql: $(psql --version 2>$null ?? 'nao instalado')"
"Docker: $(docker --version 2>$null ?? 'nao instalado')"
```

---

## 🐳 Alternativa: Tudo com Docker

Se preferir não instalar PostgreSQL localmente:

```bash
# Subir apenas o banco de dados
docker compose up -d postgres

# Verificar se está rodando
docker compose ps
```

---

## ❓ Problemas Comuns

### Python não encontrado no Windows
```batch
# Adicionar ao PATH manualmente
setx PATH "%PATH%;C:\Users\SEU_USUARIO\AppData\Local\Programs\Python\Python312"
```

### Permissão negada no Linux/macOS
```bash
chmod +x setup.sh
./setup.sh
```

### PostgreSQL: senha incorreta
Edite `.env` e verifique `DB_PASSWORD` — a senha padrão do PostgreSQL é definida durante a instalação.
