# 03 Catalogacao

Este documento resume a parte de catalogação e governança do case.

## O que já existe no projeto

- manifesto local da coleção:
  - `data/curated/catalog/dadosfera_collection.json`
- inventário de ativos:
  - `data/curated/catalog/collection_assets_inventory.csv`
- inventário de classificação:
  - `data/curated/catalog/data_classification_inventory.csv`
- ativo publicado recomendado para plataforma:
  - `data/published/dashboard/fact_orders_dashboard.csv`

## Objetivo

Demonstrar:

- organização dos ativos
- preparo para publicação
- governança mínima sobre dados e documentação

## Referencias principais

- coleção local: [docs/collection_catalog.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\collection_catalog.md)
- classificação de dados: [docs/data_classification.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\data_classification.md)
- política de governança: [docs/governance_policy.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\governance_policy.md)
- contexto de plataforma: [docs/about_dadosfera.md](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\docs\about_dadosfera.md)

## Evidencias visuais da plataforma

- importação do ativo publicado: [images/dadosfera/01_importacao_dataset.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\01_importacao_dataset.png)
- documentação e metadados do ativo: [images/dadosfera/02_catalogo_metadados.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\02_catalogo_metadados.png)
- ativo publicado dentro da coleção do case: [images/dadosfera/03_colecao_case.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\03_colecao_case.png)
- prova de volume acima de 100k registros: [images/dadosfera/04_volume_100k.png](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\images\dadosfera\04_volume_100k.png)

## Status honesto

- catalogação local: feita
- publicação real em plataforma: feita com evidência visual de importação, catálogo e volume do ativo publicado

## Ativo recomendado para upload na Dadosfera

Para execução manual na plataforma, o ativo mais adequado do projeto é:

- `data/published/dashboard/fact_orders_dashboard.csv`

Motivo:

- já representa a camada publicada do case
- evita expor a base analítica interna completa
- está alinhado ao dashboard e aos principais indicadores executivos


