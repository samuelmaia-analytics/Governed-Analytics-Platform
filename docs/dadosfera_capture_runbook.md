# Runbook de Captura da Dadosfera

Este documento define exatamente quais evidências devem ser capturadas na plataforma Dadosfera para fechar a entrega do case com prova visual real.

## Objetivo

Demonstrar de forma clara que o projeto não ficou apenas no ambiente local e que ao menos um ativo analítico foi operacionalizado na plataforma.

## Ativo recomendado para publicação

Use preferencialmente:

- `data/published/dashboard/fact_orders_dashboard.parquet`

Motivo:

- essa é a camada publicada do projeto
- ela já foi minimizada para consumo analítico
- ela é coerente com a narrativa de governança do case

## Antes de entrar na plataforma

Tenha em mãos:

- nome do projeto: `SAMUEL_MAIA_DDF_TECH_032026`
- caminho do ativo principal: `data/published/dashboard/fact_orders_dashboard.parquet`
- descrição curta do ativo:
  - `Camada publicada e minimizada para dashboard executivo do case Olist`

## Sequencia exata de capturas

### 1. Lista de ativos ou datasets

**Objetivo**

Mostrar que o ativo existe na plataforma.

**Salvar como**

`images/dadosfera/01_asset_list.png`

**O que precisa aparecer**

- nome do workspace ou área do projeto
- nome do ativo publicado
- tela de listagem ou home de datasets

### 2. Preview do dataset

**Objetivo**

Mostrar que o arquivo foi reconhecido e está acessível.

**Salvar como**

`images/dadosfera/02_asset_preview.png`

**O que precisa aparecer**

- nome do ativo
- colunas ou linhas de preview
- indicação visual de que os dados foram carregados

### 3. Esquema ou metadados do ativo

**Objetivo**

Mostrar estrutura técnica do dataset.

**Salvar como**

`images/dadosfera/03_schema.png`

**O que precisa aparecer**

- lista de colunas, schema, ou painel de metadados
- se existir, tipo de dado ou descricao do ativo

### 4. Catálogo, coleção ou tela equivalente

**Objetivo**

Mostrar a parte de descoberta, organização ou publicação do ativo.

**Salvar como**

`images/dadosfera/04_catalog.png`

**O que precisa aparecer**

- área de catálogo, coleção, classificação ou organização
- o ativo publicado dentro desse contexto

### 5. Captura opcional extra

**Objetivo**

Enriquecer a defesa se a plataforma oferecer query, notebook, app ou detalhes de uso.

**Salvar como**

`images/dadosfera/05_usage_or_query.png`

**Exemplos válidos**

- preview expandido
- query executada
- notebook aberto
- detalhe do ativo com tags, descricao ou dominio

## O que não fazer

- não publicar a `fact_orders_enriched` como evidência principal se a ideia for defender governança
- não tirar print cortado sem nome do ativo
- não usar print generico que não mostre claramente a Dadosfera

## Checklist após a captura

- os arquivos existem em `images/dadosfera/`
- o nome do ativo está visível
- a interface da plataforma está reconhecível
- ao menos uma captura mostra os dados
- ao menos uma captura mostra esquema ou catalogação

## Como usar no deck

Inserir principalmente:

- `01_asset_list.png`
- `02_asset_preview.png`
- `04_catalog.png`

Essas três imagens juntas contam a história mínima:

- o ativo foi publicado
- os dados existem e podem ser lidos
- o ativo está organizado/publicado na plataforma



