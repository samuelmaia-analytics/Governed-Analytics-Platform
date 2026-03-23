# Runbook de Captura da Dadosfera

Este documento define exatamente quais evidencias devem ser capturadas na plataforma Dadosfera para fechar a entrega do case com prova visual real.

## Objetivo

Demonstrar de forma clara que o projeto nao ficou apenas no ambiente local e que ao menos um ativo analitico foi operacionalizado na plataforma.

## Ativo recomendado para publicacao

Use preferencialmente:

- `data/published/dashboard/fact_orders_dashboard.parquet`

Motivo:

- essa e a camada publicada do projeto
- ela ja foi minimizada para consumo analitico
- ela e coerente com a narrativa de governanca do case

## Antes de entrar na plataforma

Tenha em maos:

- nome do projeto: `SAMUEL_MAIA_DDF_TECH_032026`
- caminho do ativo principal: `data/published/dashboard/fact_orders_dashboard.parquet`
- descricao curta do ativo:
  - `Camada publicada e minimizada para dashboard executivo do case Olist`

## Sequencia exata de capturas

### 1. Lista de ativos ou datasets

**Objetivo**

Mostrar que o ativo existe na plataforma.

**Salvar como**

`images/dadosfera/01_asset_list.png`

**O que precisa aparecer**

- nome do workspace ou area do projeto
- nome do ativo publicado
- tela de listagem ou home de datasets

### 2. Preview do dataset

**Objetivo**

Mostrar que o arquivo foi reconhecido e esta acessivel.

**Salvar como**

`images/dadosfera/02_asset_preview.png`

**O que precisa aparecer**

- nome do ativo
- colunas ou linhas de preview
- indicacao visual de que os dados foram carregados

### 3. Esquema ou metadados do ativo

**Objetivo**

Mostrar estrutura tecnica do dataset.

**Salvar como**

`images/dadosfera/03_schema.png`

**O que precisa aparecer**

- lista de colunas, schema, ou painel de metadados
- se existir, tipo de dado ou descricao do ativo

### 4. Catalogo, colecao ou tela equivalente

**Objetivo**

Mostrar a parte de descoberta, organizacao ou publicacao do ativo.

**Salvar como**

`images/dadosfera/04_catalog.png`

**O que precisa aparecer**

- area de catalogo, colecao, classificacao ou organizacao
- o ativo publicado dentro desse contexto

### 5. Captura opcional extra

**Objetivo**

Enriquecer a defesa se a plataforma oferecer query, notebook, app ou detalhes de uso.

**Salvar como**

`images/dadosfera/05_usage_or_query.png`

**Exemplos validos**

- preview expandido
- query executada
- notebook aberto
- detalhe do ativo com tags, descricao ou dominio

## O que nao fazer

- nao publicar a `fact_orders_enriched` como evidência principal se a ideia for defender governanca
- nao tirar print cortado sem nome do ativo
- nao usar print generico que nao mostre claramente a Dadosfera

## Checklist apos a captura

- os arquivos existem em `images/dadosfera/`
- o nome do ativo esta visivel
- a interface da plataforma esta reconhecivel
- ao menos uma captura mostra os dados
- ao menos uma captura mostra esquema ou catalogacao

## Como usar no deck

Inserir principalmente:

- `01_asset_list.png`
- `02_asset_preview.png`
- `04_catalog.png`

Essas tres imagens juntas contam a historia minima:

- o ativo foi publicado
- os dados existem e podem ser lidos
- o ativo esta organizado/publicado na plataforma
