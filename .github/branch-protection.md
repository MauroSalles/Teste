# Política de Proteção de Branch — `main`

Este documento descreve a política de proteção do branch `main` do repositório **Gelateria Sistema**.

---

## Regras obrigatórias

| Regra | Valor |
|-------|-------|
| Mudanças via Pull Request | ✅ Obrigatório |
| Reviews aprovadas antes do merge | ✅ Mínimo 1 |
| CI (lint + testes) deve passar | ✅ Obrigatório |
| Commits diretos em `main` | ❌ Proibidos |
| Force push em `main` | ❌ Proibido |
| Exclusão do branch `main` | ❌ Proibida |

---

## Como ativar no GitHub

1. Acesse **Settings → Branches → Branch protection rules**
2. Clique em **Add rule**
3. Em **Branch name pattern**, digite: `main`
4. Marque as seguintes opções:
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: **1**
     - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Adicione os checks: `lint` e `test` (do workflow `ci.yml`)
   - ✅ **Do not allow bypassing the above settings**
   - ✅ **Restrict who can push to matching branches** (somente admins)
5. Clique em **Create** (ou **Save changes**)

---

## Fluxo de trabalho aprovado

```
feature-branch → Pull Request → Review (≥1 aprovação) → CI verde → Merge em main
```

---

## Referências

- [GitHub Docs: Branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [CONTRIBUTING.md](../CONTRIBUTING.md) — Guia de contribuição detalhado
