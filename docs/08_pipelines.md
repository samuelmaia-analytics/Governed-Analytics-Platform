# 08 Pipelines

Este documento organiza a parte de pipelines do case, separando o que ja foi implementado localmente do que ainda precisa ser materializado na Dadosfera.

## Objetivo

Demonstrar a capacidade de transformar, validar e publicar dados de forma reproduzivel por meio de pipeline.

## Pipeline ja implementado localmente

O projeto ja possui um pipeline ponta a ponta em Python, orquestrado por:

- `src/run_case_pipeline.py`

Etapas disponiveis:

- `inventory`
- `profiling`
- `build`
- `publish`
- `classify`
- `contracts`
- `quality`
- `catalog`
- `queries`
- `screenshots`
- `bi`

## Artefatos gerados pelo pipeline local

- inventario bruto
- profiling exploratorio
- `fact_orders_enriched`
- `fact_orders_dashboard`
- relatorios de qualidade
- contratos de schema
- colecao local
- resultados SQL
- screenshots das queries
- exports para Power BI

## Comando principal local

```powershell
.\.venv\Scripts\python.exe src\run_case_pipeline.py
```

## Como este item deve ficar aderente ao edital

Para fechar o item 8 conforme o case da Dadosfera, ainda falta:

- criar um pipeline real dentro da plataforma
- executar esse pipeline na plataforma
- catalogar esse pipeline
- gerar evidencias visuais da execucao

## Sugestao de pipeline na Dadosfera

Pipeline minimo sugerido:

1. entrada do dataset publicado
2. etapa de tratamento ou modelagem
3. etapa de validacao
4. etapa de publicacao do ativo final

Sugestao de narrativa:

- ETL de modelagem e qualidade dos dados

## Evidencias que devem ser adicionadas depois

Salvar em `images/dadosfera/`:

- `06_pipeline_list.png`
- `07_pipeline_detail.png`
- `08_pipeline_run.png`
- `09_pipeline_catalog.png`

## Campos para preencher apos a execucao na plataforma

### Nome do pipeline na Dadosfera

- `PREENCHER`

### Objetivo do pipeline

- `PREENCHER`

### Steps utilizados

- `PREENCHER`

### Ativos de entrada

- `PREENCHER`

### Ativos de saida

- `PREENCHER`

### Link do pipeline

- `PREENCHER`

## Status atual

- pipeline local em Python: feito
- pipeline real na Dadosfera: pendente
- catalogacao do pipeline na plataforma: pendente
