# Sobre a Dadosfera

## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

## Tese Central

Neste case, a Dadosfera entra menos como substituta imediata do pipeline local e mais como camada de publicação, descoberta, compartilhamento e evolução operacional do ativo analítico.

A engenharia principal do projeto continua em Python, mas a plataforma já aparece de forma concreta em quatro frentes:

- publicação do ativo principal
- catálogo e coleção navegáveis
- sincronização programática por API
- preparação operacional para pipeline nativo e operação não interativa

## Estado Atual do Case

### Feito localmente no projeto

- ingestão dos CSVs do Olist
- promoção para `standardized`
- profiling em `staging`
- construção da `fact_orders_enriched`
- derivação da `fact_orders_dashboard`
- expansão semântica para logística, seller e cohort
- monitoramento recorrente da camada publicada
- dashboard Streamlit, SQL versionado e exportações para Power BI

### Já comprovado na plataforma

- upload/publicação do ativo principal
- catálogo e coleção materializados na interface
- screenshots da plataforma em `images/dadosfera/`

### Já implementado via integração programática

- sync de catálogo por API em `src/dadosfera_catalog_sync.py`
- autenticação não interativa por `DADOSFERA_ACCESS_TOKEN` ou `DADOSFERA_API_TOKEN`
- operador de pipelines nativos via API em `src/dadosfera_pipeline_ops.py`
- comando `deploy` idempotente para criar ou reaproveitar pipeline
- template versionado em `contracts/dadosfera/pipelines/fact_orders_dashboard_s3_parquet_pipeline.json`
- job agendado de operação da camada publicada em `.github/workflows/operate-published-layer.yml`

### Ainda não comprovado no tenant avaliado

- pipeline nativo executado na plataforma com evidência final de run
- output gerado por pipeline nativo real no tenant
- catálogo do pipeline nativo na interface

Em outras palavras: a plataforma já participa de publicação, catálogo e automação por API, mas a absorção nativa completa da transformação ainda não está comprovada.

## Por Que a Dadosfera Faz Sentido Aqui

O problema do case não é apenas transformar dados. É reduzir o tempo entre:

- chegada da fonte bruta
- preparação analítica confiável
- disponibilização para consumo
- reutilização do ativo em múltiplos canais

Em uma arquitetura puramente local, isso funciona para desenvolvimento e defesa técnica, mas escala pior quando cresce a necessidade de:

- compartilhar ativos entre consumidores
- reduzir upload e publicação manual
- manter descoberta e documentação em um ponto central
- preparar operação recorrente com menos atrito

É nesse ponto que a Dadosfera se torna economicamente e operacionalmente interessante.

## Leitura Arquitetural Correta

### Arquitetura atual do case

```text
Dataset Olist CSV
    -> pipeline local em Python
    -> raw / standardized / staging / curated
    -> fact_orders_enriched
    -> fact_orders_dashboard
    -> published semantic marts
    -> monitoramento da camada publicada
    -> Streamlit / SQL / Power BI / publicação na Dadosfera
```

### Papel atual da Dadosfera

```text
Ativo publicado e controlado
    -> publicação na plataforma
    -> catálogo e coleção
    -> sync por API
    -> preparação para operação nativa de pipeline
```

### Evolução natural com a plataforma

```text
Pipeline Python local
    -> continua como motor de transformação
    -> publica outputs governados
    -> Dadosfera centraliza descoberta, compartilhamento e operação externa
```

O desenho não exige descartar a arquitetura local. Ele permite ampliar distribuição e governança sem reabrir a modelagem já resolvida.

## Ganhos Concretos da Abordagem

### Menor atrito operacional

- menos dependência de upload manual
- catálogo mais consistente
- ativo mais fácil de localizar e compartilhar

### Governança melhor distribuída

- separação explícita entre camada interna e camada publicada
- visibilidade maior sobre o que está exposto
- preparação melhor para evolução de controle operacional

### Multiconsumo

- Streamlit
- SQL e consultas exploratórias
- BI externo
- futuras experiências analíticas na própria plataforma

### Evolução econômica

O ganho potencial não está apenas em infraestrutura. Ele está em reduzir o custo total da operação analítica:

- menos retrabalho de publicação
- menos duplicação de artefatos para consumo
- menor esforço de coordenação entre geração e distribuição do ativo

## Limite Estrutural Atual

O ponto que ainda separa “integração com a plataforma” de “pipeline nativo comprovado” é simples:

- já existe publicação comprovada
- já existe catálogo comprovado
- já existe automação por API
- ainda não existe evidência final de execução nativa do pipeline no tenant

Essa distinção precisa ser preservada para manter rigor técnico.

## Síntese Executiva

Para este case, a Dadosfera já agrega valor real como camada de publicação, catálogo e evolução operacional. O que permanece pendente não é proposta conceitual, mas evidência final de run nativo dentro da plataforma.

Essa é a leitura mais defensável:

- a engenharia local está implementada
- a publicação na plataforma está comprovada
- a automação por API está implementada
- a operação recorrente da camada publicada está empacotada
- a execução nativa do pipeline ainda precisa ser feita e evidenciada
