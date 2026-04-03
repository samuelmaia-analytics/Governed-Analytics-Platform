# Contributing

Este repositório segue um fluxo mínimo de contribuição para manter consistência entre código, dados publicados e evidências.

## Escopo

- Preserve o objetivo do projeto: transformar o dataset Olist em um ativo analítico governado, testado e consumível.
- Evite ampliar escopo com componentes de plataforma não comprovados no repositório.
- Mudanças em modelagem, publicação ou catálogo devem manter a separação entre `curated` e `published`.

## Fluxo recomendado

1. Crie uma branch a partir de `main`.
2. Faça mudanças pequenas e coesas.
3. Atualize testes, contratos e documentação impactada.
4. Execute os checks locais antes de abrir PR.

## Checks locais

```bash
python -m ruff check src streamlit_app tests
python -m pytest tests
python src/run_platform_pipeline.py --list-steps
```

## Regras de mudança

- Alterações em `src/publish_dashboard.py` exigem revisão da documentação de privacidade e governança.
- Alterações em `contracts/` exigem atualização da evidência ou relatório correspondente.
- Novos artefatos publicados devem ter dono, finalidade e camada definidos em documentação.

## Pull Requests

- Descreva o problema resolvido e o risco da mudança.
- Liste evidências de validação executadas.
- Destaque qualquer impacto em artefatos publicados, catálogo ou dashboard.
