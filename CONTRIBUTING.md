# Contributing

**Language:** `English` | [Português](#portuguese)

---

## English

This repository follows a minimal contribution flow to maintain consistency between code, published data, and governance evidence.

### Scope

- Preserve the project goal: transform the Olist dataset into a governed, tested, and consumable analytical asset.
- Avoid expanding scope with unproven platform components.
- Changes to modeling, publication, or catalog must maintain the separation between `curated` and `published` layers.

### Recommended Flow

1. Create a branch from `main`.
2. Make small, cohesive changes.
3. Update tests, contracts, and impacted documentation.
4. Run local checks before opening a PR.

### Local Checks

```bash
python -m ruff check src app tests
python -m pytest tests
python src/run_platform_pipeline.py --list-steps
```

### Change Rules

- Changes to `src/publish_dashboard.py` require reviewing privacy and governance documentation.
- Changes to `contracts/` require updating the corresponding evidence or report.
- New published artifacts must have an owner, purpose, and layer defined in documentation.

### Pull Requests

- Describe the problem solved and the risk of the change.
- List validation evidence executed.
- Highlight any impact on published artifacts, catalog, or dashboard.

---

<a name="portuguese"></a>

## Português

Este repositório segue um fluxo mínimo de contribuição para manter consistência entre código, dados publicados e evidências.

### Escopo

- Preserve o objetivo do projeto: transformar o dataset Olist em um ativo analítico governado, testado e consumível.
- Evite ampliar escopo com componentes de plataforma não comprovados no repositório.
- Mudanças em modelagem, publicação ou catálogo devem manter a separação entre `curated` e `published`.

### Fluxo Recomendado

1. Crie uma branch a partir de `main`.
2. Faça mudanças pequenas e coesas.
3. Atualize testes, contratos e documentação impactada.
4. Execute os checks locais antes de abrir PR.

### Checks Locais

```bash
python -m ruff check src app tests
python -m pytest tests
python src/run_platform_pipeline.py --list-steps
```

### Regras de Mudança

- Alterações em `src/publish_dashboard.py` exigem revisão da documentação de privacidade e governança.
- Alterações em `contracts/` exigem atualização da evidência ou relatório correspondente.
- Novos artefatos publicados devem ter dono, finalidade e camada definidos em documentação.

### Pull Requests

- Descreva o problema resolvido e o risco da mudança.
- Liste evidências de validação executadas.
- Destaque qualquer impacto em artefatos publicados, catálogo ou dashboard.
