# Publicação em Ambiente de Plataforma

Este documento registra como a publicação em ambiente de plataforma é tratada no projeto e como validar o fluxo de forma controlada.

## Objetivo

- sincronizar os ativos públicos no catálogo de plataforma
- publicar ou reaplicar a definição idempotente do pipeline de exposição
- manter evidência versionada da operação em `docs/` e nos artefatos do projeto

## Entrypoint

O fluxo é orquestrado por [`src/platform_publication.py`](../src/platform_publication.py).

Ele combina dois blocos:

- `catalog_sync`: sincroniza os ativos definidos no manifesto de catálogo
- `pipeline_publication`: garante a existência da pipeline declarada e pode disparar execução

## Arquivos usados pelo fluxo

- manifesto de catálogo: `data/curated/catalog/dadosfera_collection.json`
- definição default de pipeline: `contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json`
- relatório gerado: `docs/platform_publication.md`

## Execução recomendada

Dry run para validar autenticação, manifesto e definição antes de publicar:

```bash
python src/platform_publication.py --dry-run --target-environment prod
```

Publicação completa:

```bash
python src/platform_publication.py --target-environment prod
```

Publicação com execução imediata da pipeline:

```bash
python src/platform_publication.py --target-environment prod --execute-pipeline
```

## Variáveis de ambiente relevantes

- `DADOSFERA_ENABLED`
- `DADOSFERA_MAESTRO_BASE_URL`
- `DADOSFERA_ACCESS_TOKEN`
- `DADOSFERA_API_TOKEN`
- `DADOSFERA_USERNAME`
- `DADOSFERA_PASSWORD`
- `DADOSFERA_TOTP`
- `DADOSFERA_PIPELINE_LIST_ENDPOINT`
- `DADOSFERA_PIPELINE_CREATE_ENDPOINT`
- `DADOSFERA_PIPELINE_GET_ENDPOINT_TEMPLATE`
- `DADOSFERA_PIPELINE_RUN_ENDPOINT`
- `DADOSFERA_PIPELINE_RUNS_ENDPOINT_TEMPLATE`

## Resultado esperado

O relatório salvo pelo fluxo segue a estrutura:

| Etapa | Status | Detalhes |
| --- | --- | --- |
| `catalog_sync` | `SUCCESS` ou `DRY_RUN` | resumo dos ativos processados |
| `pipeline_publication` | `SUCCESS` ou `DRY_RUN` | id da pipeline e, quando aplicável, id da execução |

## Critérios de validação

- manifesto de catálogo carregado sem erro
- definição de pipeline com campo `name`
- autenticação válida na plataforma
- relatório final salvo em `docs/platform_publication.md`
- nenhuma divergência entre os ativos publicados e a camada local em `data/published/`

## Falhas comuns

- `HTTP 401/403`: revisar token, escopo, tenant ou credenciais
- `HTTP 404` nos endpoints de pipeline: revisar os valores `DADOSFERA_PIPELINE_*`
- definição sem `name`: ajustar o JSON da pipeline antes do deploy
- manifesto inconsistente: revisar `dadosfera_collection.json`

## Relação com o restante do projeto

A publicação em plataforma não substitui o pipeline local. Ela consome os artefatos já produzidos pelo fluxo principal e formaliza a etapa de exposição externa do produto analítico.

