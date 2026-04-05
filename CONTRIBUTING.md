# Como Contribuir — Gelateria Sistema

Bem-vindo ao repositório do **Gelateria Sistema** (Projeto Integrador). Este guia explica como contribuir de forma organizada e consistente com o MVP definido.

> ⚠️ Este é um **Projeto Integrador acadêmico**. O escopo está definido e fechado no [SCOPE.md](SCOPE.md). Antes de propor qualquer feature nova, verifique se ela está dentro do escopo.

---

## 📋 Regras de Contribuição

### 1. Toda mudança deve vir via Pull Request

**Commits diretos em `main` são proibidos.** Crie sempre um branch separado:

```bash
git checkout -b feat/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

### 2. Ao menos 1 review aprovado é obrigatório

Nenhum PR pode ser mergeado sem ao menos **1 review aprovado** por outro colaborador do projeto.

- Resolva todos os comentários de review antes do merge
- Não faça force push após solicitar review

### 3. CI (lint + testes) deve passar antes do merge

O workflow `ci.yml` executa automaticamente em cada PR:

```bash
# Lint (deve passar sem erros)
flake8 backend --count --select=E9,F63,F7,F82

# Testes (todos devem passar)
PYTHONPATH=. python -m pytest tests/ -v --tb=short
```

**Não mergeie PRs com CI falhando.** Corrija os erros antes de solicitar review.

### 4. Commits diretos em `main` são proibidos

Use sempre o fluxo: **branch → PR → review → merge**.

---

## 🏷️ Labels

Use as labels abaixo ao criar issues e PRs:

| Label | Uso |
|-------|-----|
| `bug` | Correção de comportamento incorreto |
| `enhancement` | Melhoria de feature já existente no escopo |
| `documentation` | Atualização de docs, README, comentários |
| `out-of-scope` | Feature fora do escopo do MVP (ver SCOPE.md) |
| `duplicate` | Issue/PR duplicado — fechar após identificar o original |
| `wip` | Trabalho em progresso — não mergeável ainda |

---

## 🔍 Verificando o Escopo

Antes de abrir um PR, confirme que a feature está **IN SCOPE** em [SCOPE.md](SCOPE.md).

Features **OUT OF SCOPE** (WebSocket, pagamentos, IA/ML, AR, Redis, Nginx, multi-tenant, i18n) **não serão aceitas** no MVP e devem ser rotuladas com `out-of-scope`.

---

## 🚀 Fluxo de Desenvolvimento

```
1. Abra uma Issue descrevendo o problema ou feature
2. Crie um branch: git checkout -b tipo/descricao
3. Implemente a mudança + testes
4. Abra um Pull Request com descrição clara
5. Aguarde 1 review aprovado
6. Certifique-se que CI está verde
7. Merge em main
```

---

## 🧪 Rodando Testes Localmente

```bash
pip install -r requirements.txt
PYTHONPATH=. python -m pytest tests/ -v --tb=short
```

---

## 📁 Estrutura Relevante

```
backend/           # Flask API + modelos + rotas
frontend/          # HTML/CSS/JS (páginas)
tests/             # Suite de testes pytest
database/          # Schema SQL
.github/workflows/ # CI/CD (ci.yml, deploy.yml)
SCOPE.md           # Escopo oficial do MVP
ROADMAP.md         # Roadmap e milestones
```

---

## ⚙️ Branch Protection

Consulte [.github/branch-protection.md](.github/branch-protection.md) para instruções de como ativar a proteção de branch no GitHub Settings.

---

## 📬 Contato

Dúvidas? Abra uma [Issue](https://github.com/MauroSalles/Teste/issues) com a label `documentation`.
