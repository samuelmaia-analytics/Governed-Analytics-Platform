# Executive Summary

## Objetivo do case

Transformar o dataset Olist em um ativo analítico utilizável, governado e consumível, em vez de entregar apenas uma visualização isolada.

## O que foi entregue

- pipeline reproduzível de ingestão, padronização, modelagem, qualidade e publicação
- ativo analítico interno `fact_orders_enriched`
- camada publicada `fact_orders_dashboard` para consumo executivo
- dashboard Streamlit publicado
- ativo catalogado e evidenciado na Dadosfera/Metabase
- documentação operacional, governança e runbooks

## Decisão arquitetural central

A arquitetura separa claramente duas camadas:

- `curated`: camada interna de engenharia, qualidade, SQL e exploração
- `published`: camada minimizada e controlada para consumo executivo

Essa separação evita acoplamento entre o dashboard e a camada analítica completa, reduz exposição desnecessária e melhora governança.

## Ativo principal

| Item | Valor |
| --- | --- |
| Ativo central | `fact_orders_enriched` |
| Granularidade | `1 linha por item de pedido` |
| Volume | `112.650` registros |
| Camada publicada | `fact_orders_dashboard` |
| Colunas publicadas | `22` |

## Consumo comprovado

- Streamlit público: dashboard operacional
- Dadosfera/Metabase: ativo publicado e navegável
- SQL versionado: análises reproduzíveis
- Power BI: consumo complementar

## Robustez de engenharia

Snapshot de validação em `2026-03-28`:

| Métrica | Valor |
| --- | --- |
| Testes | `114/114` passando |
| Cobertura total | `86.53%` |
| Gate mínimo | `80%` |
| Qualidade estática | `ruff check` verde |
| Entrega | CI, lint e fluxo de deploy versionados |

## Governança aplicada

- `main` protegida com pull request obrigatório
- checks obrigatórios de CI e lint
- política explícita de ownership, contribuição e segurança
- runbooks de release, rollback e operação
- pseudonimização e minimização da camada publicada

## Escopo core vs bônus

O core do case é:

- ingestão
- padronização
- modelagem analítica
- qualidade e contratos
- publicação segura
- dashboard e catálogo

Itens como GenAI e exportações auxiliares existem como extensão e não são usados para inflar o escopo principal.

## Tradeoffs deliberados

- escolha por Streamlit para acelerar consumo e prova de valor
- execução principal do pipeline fora da plataforma, com publicação comprovada na Dadosfera
- governança aplicada sem vender operação “enterprise” não implementada
- métricas de testes e cobertura devem ser lidas como snapshot operacional da data de validação, não como valor imutável do repositório

## Mensagem de defesa

“A entrega demonstra construção de produto analítico ponta a ponta: modelagem, qualidade, publicação, governança e consumo com evidência real, mantendo clareza sobre o que está automatizado e o que permanece como evolução natural.”

## Links principais

- app: `https://samuelmaia-032026.streamlit.app/`
- vídeo: `https://youtu.be/SqJ0UF1Em9k`
- coleção publicada: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- dashboard publicado: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- modelo publicado: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- tabela pública: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`
- operating model: [operating_model.md](operating_model.md)
- apresentação final: [10_apresentacao_final.md](10_apresentacao_final.md)
