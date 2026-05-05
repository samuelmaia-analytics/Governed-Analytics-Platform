# Executive Summary

## Tese

Este projeto não trata dashboard como ponto de partida. Ele trata publicação como parte do pipeline para transformar um dataset transacional em um produto analítico governado, reutilizável e consumível.

## Objetivo do projeto

Transformar o dataset Olist em um ativo analítico utilizável, governado e consumível, em vez de entregar apenas uma visualização isolada.

## O que foi entregue

- pipeline reproduzível de ingestão, padronização, modelagem, qualidade e publicação
- ativo analítico interno `fact_orders_enriched`
- camada publicada `fact_orders_dashboard` para consumo executivo
- recortes semânticos publicados para logística, seller, cohort, categoria e performance por UF
- dashboard Streamlit publicado
- ativo catalogado localmente e preparado para consumo controlado
- monitoramento recorrente da camada publicada
- alertas externos opcionais para falhas operacionais via webhook
- automação de publicação em ambiente de plataforma para catálogo e pipeline
- documentação operacional, governança e runbooks

## O Que Torna a Solução Forte

- a arquitetura separa claramente construção do ativo e exposição do ativo
- a camada publicada é minimizada e pseudonimizada antes do consumo
- o mesmo ativo publicado é reutilizado por Streamlit, Power BI e monitoramento
- a camada semântica já suporta recortes operacionais e executivos adicionais
- documentação, contratos e operação convivem no mesmo repositório

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
| Colunas publicadas | `34` |

## Consumo comprovado

- Streamlit público: dashboard operacional
- SQL versionado: análises reproduzíveis
- Power BI: consumo complementar

## Leitura de Negócio

Na prática, a solução responde perguntas executivas sobre receita, atraso, categorias, geografia e pagamento sem depender de lógica escondida no dashboard. O consumo é consequência de uma modelagem explícita, não o contrário.

## Robustez de engenharia

Snapshot de validação em `2026-03-29`:

| Métrica | Valor |
| --- | --- |
| Testes | `124/124` passando |
| Cobertura total | `83.71%` |
| Gate mínimo | `80%` |
| Qualidade estática | `ruff check` verde |
| Operação | CI, lint e fluxo de deploy versionados |

## Governança aplicada

- `main` protegida com pull request obrigatório
- checks obrigatórios de CI e lint
- política explícita de ownership, contribuição e segurança
- runbooks de release, rollback e operação
- pseudonimização e minimização da camada publicada
- alertas externos opcionais para incidentes operacionais
- publicação em plataforma com sync de catálogo e pipeline

## Escopo principal e extensões

O núcleo do projeto é:

- ingestão
- padronização
- modelagem analítica
- qualidade e contratos
- publicação segura
- dashboard e catálogo

Itens como GenAI e exportações auxiliares existem como extensões e não redefinem o escopo principal.

## Tradeoffs deliberados

- escolha por Streamlit para acelerar consumo e prova de valor
- execução principal do pipeline centrada no ambiente local e em artefatos versionados
- governança aplicada sem vender operação “enterprise” não implementada
- métricas de testes e cobertura devem ser lidas como snapshot operacional da data de validação, não como valor imutável do repositório

## Leitura Recomendada

1. [architecture.md](architecture.md)
2. [operating_model.md](operating_model.md)
3. [privacy_governance.md](privacy_governance.md)
4. [10_apresentacao_final.md](10_apresentacao_final.md)

## Risco residual

O principal risco remanescente não está em modelagem ou consumo, mas em evolução operacional futura. O projeto já organiza esse passo em camadas, monitoramento e contratos, mas integrações externas continuam opcionais e fora do núcleo principal.

## Mensagem de defesa

“O projeto demonstra construção de produto analítico ponta a ponta: modelagem, qualidade, publicação, governança e consumo com evidência real, mantendo clareza sobre o que está automatizado e o que permanece como evolução natural.”

## Links principais

- app: `https://governed-analytics-platform.streamlit.app/`
- vídeo: `https://youtu.be/SqJ0UF1Em9k`
- operating model: [operating_model.md](operating_model.md)
- apresentação final: [10_apresentacao_final.md](10_apresentacao_final.md)

