# 🤝 Guia de Contribuição — Gelateria Pro

Obrigado por querer contribuir! Este guia explica como colaborar com o projeto.

---

## 📋 Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Git configurado com nome e email

---

## 🚀 Configuração do Ambiente

```bash
# 1. Faça um fork e clone o repositório
git clone https://github.com/seu-usuario/gelateria-pro.git
cd gelateria-pro

# 2. Crie um ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Suba o banco de dados
docker compose up db -d

# 5. Execute os testes
PYTHONPATH=. pytest tests/ -v
```

---

## 🌿 Fluxo de Trabalho

1. **Crie uma branch** a partir de `main`:
   ```bash
   git checkout -b feature/minha-funcionalidade
   # ou
   git checkout -b fix/correcao-bug
   ```

2. **Implemente suas alterações** seguindo os padrões do projeto

3. **Execute os testes** e certifique-se que passam:
   ```bash
   PYTHONPATH=. pytest tests/ -v --tb=short
   flake8 backend --count --select=E9,F63,F7,F82
   ```

4. **Faça commits** com mensagens claras:
   ```bash
   git commit -m "feat: adiciona serviço de notificação por SMS"
   git commit -m "fix: corrige validação de cupom expirado"
   ```

5. **Abra um Pull Request** usando o template fornecido

---

## 📐 Padrões de Código

### Python
- Siga o **PEP 8** (use `flake8` para verificar)
- Use **type hints** sempre que possível
- Docstrings em funções públicas
- Queries SQL com **parâmetros preparados**: `cursor.execute("SELECT ... WHERE id = %s", (id,))`
- Respostas de erro: `jsonify({"error": "mensagem"}), status_code`

### JavaScript
- Use `textContent` (nunca `innerHTML`) para conteúdo do usuário
- Funções assíncronas com `async/await`
- Sem bibliotecas externas desnecessárias no frontend

### Testes
- Use `unittest.mock.patch` para mockar `get_db` — nunca acesse o banco real nos testes
- Crie testes para todos os novos endpoints
- Mantenha cobertura acima de 70%

---

## 🐛 Reportando Bugs

Abra uma [issue](../../issues/new) com:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs. atual
- Versão do Python e sistema operacional

---

## 💡 Sugerindo Funcionalidades

Abra uma [issue](../../issues/new) com:
- Descrição da funcionalidade
- Caso de uso e motivação
- Proposta de implementação (opcional)

---

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a [MIT License](LICENSE).
