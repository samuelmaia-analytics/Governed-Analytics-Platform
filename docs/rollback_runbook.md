# Rollback Runbook

Este runbook define a resposta mínima para rollback do case quando uma alteração afeta dashboard, camada publicada ou artefatos de evidência.

## Gatilhos de rollback

- dashboard indisponível ou quebrado após promoção
- artefato publicado com schema incorreto ou colunas indevidas
- falha em pseudonimização ou regressão de governança
- divergência grave entre docs, dados publicados e comportamento do app

## Procedimento

1. Identificar o último commit estável em `main`.
2. Reverter com commit explícito, sem reescrever histórico.
3. Reexecutar:

```bash
python -m ruff check src streamlit_app tests
python -m pytest tests
```

4. Se necessário, regenerar a camada publicada:

```bash
python src/run_case_pipeline.py --steps build publish quality contracts
```

5. Revalidar o workflow de promoção para `streamlit-prod`.
6. Se o app estiver apontando temporariamente para `streamlit-prod`, confirmar se o branch publicado já recebeu o commit de rollback ou se o apontamento precisa ser ajustado manualmente no Streamlit Cloud.

## Evidências mínimas após rollback

- dashboard carregando
- camada `published/dashboard` íntegra
- contratos e quality checks válidos
- documentação central sem inconsistência óbvia
