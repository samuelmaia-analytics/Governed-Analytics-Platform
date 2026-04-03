# Runbook de Captura do Dashboard Streamlit


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/olist-governed-analytics-platform`
- Dashboard Streamlit: `https://olist-governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento define exatamente quais capturas finais devem ser feitas no dashboard para fechar a entrega do projeto.

## Pre-condições

- a virtualenv deve estar ativa ou acessível em `.venv`
- a camada publicada deve existir em `data/published/dashboard/fact_orders_dashboard.parquet`
- o app deve ser iniciado a partir da raiz do projeto

## Comando para subir o app

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app\app.py
```

## Validação inicial

Antes de tirar qualquer print, confirme:

- o app abre sem erro
- os KPIs aparecem
- os filtros laterais estão visíveis
- o dashboard responde a troca de filtros

## Sequencia exata de capturas

### 1. Visão geral do dashboard

**Objetivo**

Mostrar a tela principal completa, com identidade visual, filtros e KPIs.

**Como configurar**

- manter o intervalo completo de datas
- deixar `Todas as categorias`
- deixar `Todos os estados`
- deixar `Todos os status`
- deixar `Todos os meios`
- manter `Dimensão geográfica = Cliente`
- manter o modo normal, não o modo apresentação
- deixar a navegação em `Visão completa`

**Salvar como**

`images/dashboard/01_overview.png`

**Tem que aparecer no print**

- cabeçalho do dashboard
- barra lateral com filtros
- primeira faixa de KPIs
- início da área analítica principal

### 2. KPIs executivos

**Objetivo**

Destacar os indicadores principais do projeto.

**Como configurar**

- manter os mesmos filtros globais da captura 1
- rolar a tela para centralizar a faixa de KPIs

**Salvar como**

`images/dashboard/02_kpis.png`

**Tem que aparecer no print**

- cards de KPI
- variação ou comparativo, se visivel
- parte mínima do contexto acima

### 3. Análise temporal

**Objetivo**

Mostrar a evolução do negócio ao longo do tempo.

**Como configurar**

- manter os filtros globais abertos
- na navegação, selecionar `Tempo`

**Salvar como**

`images/dashboard/03_temporal.png`

**Tem que aparecer no print**

- gráfico temporal principal
- algum subtítulo ou contexto da seção
- preferencialmente a legenda, se existir

### 4. Análise por categorias

**Objetivo**

Mostrar concentração de receita por categoria.

**Como configurar**

- na navegação, selecionar `Categorias`
- se quiser destacar um recorte, use uma categoria específica com alto volume, mas prefira a visão completa

**Salvar como**

`images/dashboard/04_categories.png`

**Tem que aparecer no print**

- gráfico principal da seção
- nomes de categorias legíveis
- valores ou ranking, se visivel

### 5. Analise geográfica

**Objetivo**

Mostrar distribuição regional da operação.

**Como configurar**

- na navegação, selecionar `Regional`
- manter `Dimensão geográfica = Cliente`
- se o visual ficar melhor, repetir uma segunda versão com `Seller` para uso opcional na apresentação

**Salvar como**

`images/dashboard/05_geography.png`

**Tem que aparecer no print**

- gráfico ou mapa principal da seção
- estados visíveis
- indicação clara de que a visao e geográfica

## Captura opcional extra

Se houver tempo, gere mais uma captura para enriquecer o deck:

- `images/dashboard/06_filtered_view.png`

Configuração sugerida:

- intervalo em 2018
- `Categoria específica`
- escolher uma categoria relevante
- `UF específica`
- escolher `SP`

Objetivo:

Mostrar que o app suporta exploração orientada por filtro.

## Checklist final após as capturas

- os 5 arquivos existem em `images/dashboard/`
- todos os textos principais estão legíveis
- nenhum print mostra erro ou área em branco
- o browser não está com zoom estranho
- a interface da máquina não expõe itens desnecessários

## Observação importante

Essas capturas devem ser feitas manualmente na interface. Este repositório agora já está preparado para receber os arquivos nos caminhos corretos.




