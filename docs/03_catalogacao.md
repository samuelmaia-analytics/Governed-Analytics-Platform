# 03 Catalogacao

Este documento resume a parte de catalogacao e governanca do case.

## O que ja existe no projeto

- manifesto local da colecao:
  - `data/curated/catalog/dadosfera_collection.json`
- inventario de ativos:
  - `data/curated/catalog/collection_assets_inventory.csv`
- inventario de classificacao:
  - `data/curated/catalog/data_classification_inventory.csv`
- ativo publicado recomendado para plataforma:
  - `data/published/dashboard/fact_orders_dashboard.csv`

## Objetivo

Demonstrar:

- organizacao dos ativos
- preparo para publicacao
- governanca minima sobre dados e documentacao

## Referencias principais

- colecao local: [docs/collection_catalog.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\collection_catalog.md)
- classificacao de dados: [docs/data_classification.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\data_classification.md)
- politica de governanca: [docs/governance_policy.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\governance_policy.md)
- contexto de plataforma: [docs/about_dadosfera.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\about_dadosfera.md)

## Evidencias visuais da plataforma

- importacao do ativo publicado: [images/dadosfera/01_importacao_dataset.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\01_importacao_dataset.png)
- documentacao e metadados do ativo: [images/dadosfera/02_catalogo_metadados.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\02_catalogo_metadados.png)
- ativo publicado dentro da colecao do case: [images/dadosfera/03_colecao_case.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\03_colecao_case.png)
- prova de volume acima de 100k registros: [images/dadosfera/04_volume_100k.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\04_volume_100k.png)

## Status honesto

- catalogacao local: feita
- publicacao real em plataforma: feita com evidencia visual de importacao, catalogo e volume do ativo publicado

## Ativo recomendado para upload na Dadosfera

Para execucao manual na plataforma, o ativo mais adequado do projeto e:

- `data/published/dashboard/fact_orders_dashboard.csv`

Motivo:

- ja representa a camada publicada do case
- evita expor a base analitica interna completa
- esta alinhado ao dashboard e aos principais indicadores executivos
