# 🍦 Sistema de Gelateria

Sistema de gerenciamento de gelateria com interface estilo terminal (CMD), backend Python/Flask e banco de dados PostgreSQL.

---

## 🚀 Início Rápido

```bash
# 1. Clone o repositório
git clone https://github.com/MauroSalles/Teste.git
cd Teste

# 2. Execute o setup automático (macOS/Linux)
chmod +x setup.sh
./setup.sh

# 3. Configure suas credenciais
nano .env   # ou abra no VS Code

# 4. Inicie o ambiente de desenvolvimento
./start-dev.sh

# 5. Acesse
#    Backend:  http://localhost:5000
#    Frontend: http://localhost:3000
```

**Windows?** Execute `setup.bat` em vez de `./setup.sh`.

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [REQUISITOS.md](REQUISITOS.md) | Pré-requisitos e como instalar cada programa |
| [SETUP_LOCAL.md](SETUP_LOCAL.md) | Guia completo de configuração do ambiente local |
| [TROUBLESHOOTING_VERCEL.md](TROUBLESHOOTING_VERCEL.md) | Solução para problemas de vinculação com Vercel |

---

## 📁 Estrutura do Projeto

```
Teste/
├── backend/           # API Flask
│   └── app.py
├── frontend/          # Interface web
├── .env.example       # Modelo de variáveis de ambiente
├── requirements.txt   # Dependências Python
├── setup.sh           # Setup automático (macOS/Linux)
├── setup.bat          # Setup automático (Windows)
├── start-dev.sh       # Iniciar ambiente de desenvolvimento
├── start-postgres.sh  # Iniciar PostgreSQL
├── REQUISITOS.md      # Pré-requisitos detalhados
├── SETUP_LOCAL.md     # Guia de configuração local
└── TROUBLESHOOTING_VERCEL.md  # Troubleshooting Vercel
```

---

## 🌐 Deploy em Produção

| Serviço | Propósito | Link |
|---------|-----------|------|
| [Render](https://render.com) | Backend + PostgreSQL | https://render.com |
| [Vercel](https://vercel.com) | Frontend | https://vercel.com |
| [Netlify](https://netlify.com) | Frontend (alternativa ao Vercel) | https://netlify.com |

> Com problemas no Vercel? Veja [TROUBLESHOOTING_VERCEL.md](TROUBLESHOOTING_VERCEL.md).

---

## 🛠️ Tecnologias

- **Backend**: Python 3.9+, Flask 2.3, PostgreSQL 12+
- **Frontend**: HTML, CSS, JavaScript
- **Deploy**: Render (backend), Vercel/Netlify (frontend)
- **CI/CD**: GitHub Actions

---

## 📄 Licença

Este projeto está sob a licença MIT — veja o arquivo [LICENSE](LICENSE) para detalhes.
