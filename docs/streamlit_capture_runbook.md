# Runbook de Captura do Dashboard Streamlit

Este documento define exatamente quais capturas finais devem ser feitas no dashboard para fechar a entrega do case.

## Pre-condicoes

- a virtualenv deve estar ativa ou acessivel em `.venv`
- a camada publicada deve existir em `data/published/dashboard/fact_orders_dashboard.parquet`
- o app deve ser iniciado a partir da raiz do projeto

## Comando para subir o app

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app\app.py
```

## Validacao inicial

Antes de tirar qualquer print, confirme:

- o app abre sem erro
- os KPIs aparecem
- os filtros laterais estao visiveis
- o dashboard responde a troca de filtros

## Sequencia exata de capturas

### 1. Visao geral do dashboard

**Objetivo**

Mostrar a tela principal completa, com identidade visual, filtros e KPIs.

**Como configurar**

- manter o intervalo completo de datas
- deixar `Todas as categorias`
- deixar `Todos os estados`
- deixar `Todos os status`
- deixar `Todos os meios`
- manter `Dimensão geográfica = Cliente`
- manter o modo normal, nao o modo apresentacao
- deixar a navegacao em `Visão completa`

**Salvar como**

`images/dashboard/01_overview.png`

**Tem que aparecer no print**

- cabecalho do dashboard
- barra lateral com filtros
- primeira faixa de KPIs
- inicio da area analitica principal

### 2. KPIs executivos

**Objetivo**

Destacar os indicadores principais do case.

**Como configurar**

- manter os mesmos filtros globais da captura 1
- rolar a tela para centralizar a faixa de KPIs

**Salvar como**

`images/dashboard/02_kpis.png`

**Tem que aparecer no print**

- cards de KPI
- variacao ou comparativo, se visivel
- parte minima do contexto acima

### 3. Analise temporal

**Objetivo**

Mostrar a evolucao do negocio ao longo do tempo.

**Como configurar**

- manter os filtros globais abertos
- na navegacao, selecionar `Tempo`

**Salvar como**

`images/dashboard/03_temporal.png`

**Tem que aparecer no print**

- grafico temporal principal
- algum subtitulo ou contexto da secao
- preferencialmente a legenda, se existir

### 4. Analise por categorias

**Objetivo**

Mostrar concentracao de receita por categoria.

**Como configurar**

- na navegacao, selecionar `Categorias`
- se quiser destacar um recorte, use uma categoria especifica com alto volume, mas prefira a visao completa

**Salvar como**

`images/dashboard/04_categories.png`

**Tem que aparecer no print**

- grafico principal da secao
- nomes de categorias legiveis
- valores ou ranking, se visivel

### 5. Analise geografica

**Objetivo**

Mostrar distribuicao regional da operacao.

**Como configurar**

- na navegacao, selecionar `Regional`
- manter `Dimensão geográfica = Cliente`
- se o visual ficar melhor, repetir uma segunda versao com `Seller` para uso opcional na apresentacao

**Salvar como**

`images/dashboard/05_geography.png`

**Tem que aparecer no print**

- grafico ou mapa principal da secao
- estados visiveis
- indicacao clara de que a visao e geografica

## Captura opcional extra

Se houver tempo, gere mais uma captura para enriquecer o deck:

- `images/dashboard/06_filtered_view.png`

Configuracao sugerida:

- intervalo em 2018
- `Categoria específica`
- escolher uma categoria relevante
- `UF específica`
- escolher `SP`

Objetivo:

Mostrar que o app suporta exploracao orientada por filtro.

## Checklist final apos as capturas

- os 5 arquivos existem em `images/dashboard/`
- todos os textos principais estao legiveis
- nenhum print mostra erro ou area em branco
- o browser nao esta com zoom estranho
- a interface da maquina nao expoe itens desnecessarios

## Observacao importante

Essas capturas devem ser feitas manualmente na interface. Este repositório agora ja esta preparado para receber os arquivos nos caminhos corretos.
