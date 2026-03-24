# Evidência da Query Principal

## Objetivo da query

Este documento registra a query principal utilizada para sustentar os indicadores e recortes analíticos do dashboard Power BI do case.

Ela foi estruturada para cobrir, de forma rastreável e defensável:

- Receita Total
- Total de Pedidos
- Ticket Médio
- Review Médio
- % Pedidos em Atraso
- Evolução da Receita no Tempo
- Top 10 Categorias por Receita
- Distribuição dos Pedidos por Status
- Estados com Maior Percentual de Atraso
- Top 10 Categorias por Frete Médio
- Detalhamento por Categoria

## Breve explicação da lógica

A SQL parte da tabela analítica `fact_orders_enriched`, que já consolida o domínio de pedidos, itens, clientes, sellers, pagamentos, reviews e variáveis derivadas de operação.

Em vez de uma única consulta monolítica, o arquivo foi organizado em blocos independentes. Isso melhora:

- legibilidade
- manutenção
- auditoria do racional analítico
- reutilização por visual ou por KPI

## Bloco da SQL usada

Arquivo de referência:

- [query_principal.sql](C:\Users\samue\PycharmProjects\SAMUEL_MAIA_DDF_TECH_032026\sql\query_principal.sql)

```sql
-- Referência completa em sql/query_principal.sql
-- O arquivo contem os blocos de:
-- 1. KPIs Executivos
-- 2. Evolucao da Receita no Tempo
-- 3. Top 10 Categorias por Receita
-- 4. Distribuicao dos Pedidos por Status
-- 5. Estados com Maior Percentual de Atraso
-- 6. Top 10 Categorias por Frete Medio
-- 7. Detalhamento por Categoria
```

## Onde inserir o print do resultado

Inserir abaixo o print da execução da query principal ou da consulta mais relevante utilizada para construir o dashboard.

Marcador para inserção manual:

`[INSERIR PRINT DO RESULTADO DA QUERY PRINCIPAL AQUI]`

Sugestão de nome do arquivo:

- `powerbi/query_principal_resultado.png`

## Breve leitura analítica dos resultados

Leitura executiva sugerida:

- os KPIs sintetizam a dimensão econômica, operacional e de experiência do cliente
- a visão temporal permite identificar sazonalidade e ritmo de geração de receita
- a leitura por categoria mostra concentração de valor e espaço para otimização de portfólio
- a análise por status ajuda a separar receita entregue de fricções operacionais
- a leitura por estado adiciona contexto geográfico para atraso e performance comercial

## Status

Documento pronto.

Ponto pendente de validação:

- inserção do print final do resultado SQL
