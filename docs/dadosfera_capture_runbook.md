# Runbook de Captura da Dadosfera


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento define exatamente quais evidências devem ser capturadas na plataforma Dadosfera para fechar a entrega do case com prova visual real.

## Objetivo

Demonstrar de forma clara que o projeto não ficou apenas no ambiente local e que ao menos um ativo analítico foi operacionalizado na plataforma.

## Ativo recomendado para publicação

Use preferencialmente:

- `data/published/dashboard/fact_orders_dashboard.csv`

Motivo:

- essa é a camada publicada do projeto
- ela já foi minimizada para consumo analítico
- ela é coerente com a narrativa de governança do case
- facilita upload manual e inspeção tabular na plataforma

## Antes de entrar na plataforma

Tenha em mãos:

- nome do projeto: `SAMUEL_MAIA_DDF_TECH_032026`
- caminho do ativo principal: `data/published/dashboard/fact_orders_dashboard.csv`
- descrição curta do ativo:
  - `Camada publicada e minimizada para dashboard executivo do case Olist`

## Sequencia exata de capturas

### 1. Importacao do dataset

**Objetivo**

Mostrar o momento de carga do arquivo publicado na plataforma.

**Salvar como**

`images/dadosfera/01_importacao_dataset.png`

**O que precisa aparecer**

- nome do arquivo ou ativo publicado
- tela de importacao, upload ou confirmacao inicial
- contexto visivel de que a acao ocorreu dentro da plataforma

### 2. Catalogo e metadados do ativo

**Objetivo**

Mostrar que o ativo foi reconhecido, estruturado e catalogado.

**Salvar como**

`images/dadosfera/02_catalogo_metadados.png`

**O que precisa aparecer**

- nome do ativo
- colunas, schema ou painel de metadados
- indicacao visual de classificacao ou descricao do ativo

### 3. Colecao do case

**Objetivo**

Mostrar o ativo dentro da colecao publicada do case.

**Salvar como**

`images/dadosfera/03_colecao_case.png`

**O que precisa aparecer**

- nome da colecao
- ativo publicado dentro do contexto da colecao
- navegacao ou organizacao reconhecivel da plataforma

### 4. Evidencia de volume relevante

**Objetivo**

Mostrar que o ativo publicado possui escala compativel com a narrativa do case.

**Salvar como**

`images/dadosfera/04_volume_100k.png`

**O que precisa aparecer**

- total de linhas, volume processado ou indicador equivalente
- nome do ativo publicado
- contexto da plataforma visivel

### 5. Captura opcional extra

**Objetivo**

Enriquecer a defesa com uma visao mais executiva do que ja foi publicado.

**Salvar como**

`images/dadosfera/dadosfera_dashboard_final.png`

**Exemplos válidos**

- dashboard publicado
- lista de ativos publicados
- query executada na plataforma
- detalhe adicional do ativo com contexto de uso

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

- `01_importacao_dataset.png`
- `02_catalogo_metadados.png`
- `03_colecao_case.png`

Essas três imagens juntas contam a história mínima:

- o ativo foi carregado na plataforma
- o ativo foi descrito e catalogado
- o ativo foi organizado dentro da colecao do case



