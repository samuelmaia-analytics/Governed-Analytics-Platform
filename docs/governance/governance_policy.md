# Política de Governança, Publicação e Retenção


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/Governed-Analytics-Platform`
- Dashboard Streamlit: `https://governed-analytics-platform.streamlit.app/`
- Coleção na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/collection/1101-samuel-maia-03-2026`
- Dashboard na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/dashboard/294-dashboard-executivo-de-vendas`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`
- Tabela pública na Dadosfera: `https://app.dadosfera.ai/pt-BR/catalog/data-assets/2d044685-b897-4cfb-8010-b8c19c1e669d`

## Objetivo

Este documento define as regras mínimas de governança aplicadas ao projeto `olist_governed_analytics_platform`, com foco em classificação da informação, separação por camadas, publicação controlada, retenção e accountability.

## Papéis e Responsabilidades

| Papel | Responsabilidade |
| --- | --- |
| `Data Owner` | Responsável pelo objetivo analítico do ativo e pela aprovação de uso publicado. |
| `Data Steward` | Responsável pelo catálogo, dicionário de dados, regras de qualidade e classificação. |
| `Analytics Engineer` | Responsável pela transformação, modelagem, testes e publicação técnica das camadas. |
| `Consumer` | Responsável por consumir apenas a camada apropriada ao caso de uso. |

No contexto deste projeto, os papéis estão acumulados pelo autor do projeto, mas foram explicitados para refletir governança corporativa real.

## Classificação da Informação

| Classe | Definição | Exemplo no projeto | Tratamento |
| --- | --- | --- | --- |
| `Pública` | Informação pronta para divulgação sem restrição relevante. | documentação final do projeto, screenshots de queries agregadas | pode ser publicada no GitHub |
| `Interna` | Informação técnica de apoio ao pipeline, sem necessidade de exposição externa. | profiling, quality checks detalhados, tabela analítica interna | uso restrito ao projeto |
| `Sensível Analítica` | Informação que não identifica diretamente, mas aumenta risco por granularidade e combinação. | IDs transacionais, cidades, CEP prefixado, timestamps detalhados | pseudonimizar, agregar ou remover da camada publicada |

## Política por Camada

| Camada | Finalidade | Regra de acesso/publicação |
| --- | --- | --- |
| `raw/landing` | preservação da fonte | não é camada de exposição; uso técnico e reprodutibilidade |
| `standardized` | reuso técnico padronizado | interna ao pipeline |
| `staging` | profiling e diagnósticos | interna ao pipeline |
| `curated/analytics` | base analítica interna | não deve ser consumida diretamente por front-end ou material publicado |
| `curated/ops` | rastreabilidade operacional | uso interno para observabilidade de jobs e execução |
| `published/dashboard` | consumo do produto analítico | camada oficial do Streamlit e de exposição executiva |
| `published/semantic` | recortes agregados publicados | consumo analítico derivado sem expor a granularidade completa |
| `published/monitoring` | observabilidade da camada publicada | uso operacional e de governança; não é camada de apresentação executiva |

## Política de Minimização

- IDs diretos ou transacionais não devem ser expostos na camada publicada sem pseudonimização.
- Cidade e prefixo de CEP não devem ser publicados no dashboard quando UF resolve a pergunta de negócio.
- O dashboard deve priorizar agregações por categoria, período, UF, pagamento e status.
- Drill-down detalhado deve usar apenas chaves pseudonimizadas e não dados de localização fina.

## Política de Retenção e Descarte

| Ativo | Política |
| --- | --- |
| `raw/landing` | mantido enquanto necessário para reproduzir o projeto |
| `standardized` | regenerável; pode ser descartado e recriado |
| `staging` | regenerável; pode ser descartado e recriado |
| `curated/analytics` | mantido como camada interna do pipeline |
| `curated/ops` | regenerável; manter histórico conforme necessidade operacional do projeto |
| `published/dashboard` | regenerável; publicar apenas a versão vigente do dashboard |
| `published/semantic` | regenerável; manter apenas a versão compatível com a camada publicada vigente |
| `published/monitoring` | regenerável; manter histórico conforme necessidade de observabilidade e auditoria |
| `screenshots/query_results` | mantidos por fazerem parte da documentação do projeto |

## Rastreabilidade e Accountability

- toda transformação principal possui script versionado em `src/`
- a coleção local em `data/curated/catalog/` registra os ativos do projeto
- a qualidade da camada analítica é registrada em `docs/data_quality_report.md`
- a política de publicação segura é registrada em `docs/privacy_governance.md`
- contratos simples de schema validam estrutura mínima em `standardized`, `curated` e `published`
- ownership mínimo do repositório foi formalizado em `.github/CODEOWNERS`
- fluxo de contribuição e validação local foi formalizado em `CONTRIBUTING.md`
- tratamento de incidentes e exposição indevida foi formalizado em `SECURITY.md`

## Limitações

- este projeto não implementa autenticação, RBAC ou catálogo externo real
- os controles aqui documentados representam uma implementação local de governança por design adequada ao escopo do projeto




