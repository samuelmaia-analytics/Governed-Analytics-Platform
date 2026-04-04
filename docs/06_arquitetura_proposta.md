# 06 Arquitetura Proposta

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/governed-analytics-platform`
- Dashboard Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

Este documento resume a arquitetura implementada hoje e a evolução proposta com maior absorção da plataforma, sem confundir o que já está operacionalizado com o que ainda depende de evidência externa.

## Arquitetura Implementada Hoje

```text
raw -> standardized -> staging -> curated -> published/dashboard -> published/semantic + published/monitoring -> consumo
```

Leitura correta:

- a arquitetura local já está implementada
- a camada publicada já está comprovada externamente
- a operação recorrente da camada publicada já está empacotada
- a plataforma já participa de catálogo, publicação e automação por API

## Evolução Proposta com Plataforma

```text
fontes -> pipeline local ou pipeline nativo -> ativo publicado -> catálogo e distribuição na plataforma -> consumo por app, SQL e BI
```

## O Que Já Foi Absorvido Pela Plataforma

- publicação do ativo principal
- catálogo e coleção navegáveis
- sync de ativos públicos via API
- autenticação não interativa por token para automação
- preparação operacional para criar e executar pipeline por API

## O Que Ainda Depende de Evidência Externa

- execução nativa de pipeline real no tenant
- output gerado por esse pipeline nativo
- catálogo do pipeline nativo na interface

Essa distinção é a base da leitura tecnicamente rigorosa do projeto.

## Arquitetura-Alvo Mais Madura

```text
fontes
    -> ingestão e transformação
    -> ativo governado
    -> camada publicada
    -> monitoramento recorrente
    -> catálogo e distribuição
    -> consumidores múltiplos
```

Nesse cenário, a plataforma deixaria de atuar apenas como camada de publicação e passaria a absorver parte maior da operação recorrente.

## Referências

- arquitetura atual: [docs/architecture.md](./architecture.md)
- contexto de plataforma: [docs/about_dadosfera.md](./about_dadosfera.md)
- pipelines: [docs/08_pipelines.md](./08_pipelines.md)

