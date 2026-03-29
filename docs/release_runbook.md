# Release Runbook

Este runbook resume o fluxo mínimo de release do case para manter consistência entre código, artefatos de dados, dashboard e documentação publicada.

## Objetivo

- garantir que a branch principal esteja íntegra antes de promover o deploy
- evitar divergência entre camada publicada, evidências e narrativa do case
- deixar rollback e revalidação explícitos

## Pré-release

1. Confirmar que a branch está atualizada com `main`.
2. Confirmar que a mudança que será publicada está mergeada em `main`, já que `main` é a origem da promoção automática para `streamlit-prod`.
3. Executar:

```bash
python -m ruff check src streamlit_app tests
python -m pytest tests
python src/run_case_pipeline.py --list-steps
```

4. Se a mudança impactar dados publicados, regenerar os artefatos críticos:

```bash
python src/run_case_pipeline.py --steps build publish quality contracts catalog queries bi
```

5. Revisar se os arquivos abaixo refletem a mudança:
- `data/published/dashboard/fact_orders_dashboard.parquet`
- `data/published/dashboard/fact_orders_dashboard.csv`
- `docs/privacy_governance.md`
- `docs/data_quality_report.md`
- `docs/schema_contract_report.md`

## Critérios de promoção

- `CI` verde
- `Lint` verde
- cobertura acima do threshold configurado no projeto
- nenhuma divergência relevante entre docs geradas e artefatos publicados

## Deploy

1. Fazer merge em `main`.
2. Confirmar `CI` verde em `main`.
3. Confirmar execução do workflow `Deploy Streamlit`, que promove o commit validado para `streamlit-prod`.
4. Validar o app Streamlit e os principais links públicos do case.
5. Se houver incidente de publicação no branch principal do app, usar `streamlit-prod` como fallback explícito no Streamlit Cloud até normalização.

## Pós-release

- revisar se o dashboard abre corretamente
- validar os filtros principais e a navegação executiva
- validar se a camada publicada segue pseudonimizada e minimizada
