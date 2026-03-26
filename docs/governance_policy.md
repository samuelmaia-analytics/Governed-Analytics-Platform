# Política de Governança, Publicação e Retenção


## Acesso Rápido

- Repositório: `https://github.com/samuelmaia-analytics/SAMUEL_MAIA_DDF_TECH_032026`
- Dashboard Streamlit: `https://samuelmaia-032026.streamlit.app/`
- Ativo principal na Dadosfera: `https://metabase-treinamentos.dadosfera.ai/model/2719-fact-orders-dashboard`

## Objetivo

Este documento define as regras mínimas de governança aplicadas ao projeto `samuelmaia_DDF_032026`, com foco em classificação da informação, separação por camadas, publicação controlada, retenção e accountability.

## Papéis e Responsabilidades

| Papel | Responsabilidade |
| --- | --- |
| `Data Owner` | Responsável pelo objetivo analítico do ativo e pela aprovação de uso publicado. |
| `Data Steward` | Responsável pelo catálogo, dicionário de dados, regras de qualidade e classificação. |
| `Analytics Engineer` | Responsável pela transformação, modelagem, testes e publicação técnica das camadas. |
| `Consumer` | Responsável por consumir apenas a camada apropriada ao caso de uso. |

No contexto deste case, os papéis estão acumulados pelo autor do projeto, mas foram explicitados para refletir governança corporativa real.

## Classificação da Informação

| Classe | Definição | Exemplo no projeto | Tratamento |
| --- | --- | --- | --- |
| `Pública` | Informação pronta para divulgação sem restrição relevante. | documentação final do case, screenshots de queries agregadas | pode ser publicada no GitHub |
| `Interna` | Informação técnica de apoio ao pipeline, sem necessidade de exposição externa. | profiling, quality checks detalhados, tabela analítica interna | uso restrito ao projeto |
| `Sensível Analítica` | Informação que não identifica diretamente, mas aumenta risco por granularidade e combinação. | IDs transacionais, cidades, CEP prefixado, timestamps detalhados | pseudonimizar, agregar ou remover da camada publicada |

## Política por Camada

| Camada | Finalidade | Regra de acesso/publicação |
| --- | --- | --- |
| `raw/landing` | preservação da fonte | não é camada de exposição; uso técnico e reprodutibilidade |
| `standardized` | reuso técnico padronizado | interna ao pipeline |
| `staging` | profiling e diagnósticos | interna ao pipeline |
| `curated/analytics` | base analítica interna | não deve ser consumida diretamente por front-end ou material publicado |
| `published/dashboard` | consumo do produto analítico | camada oficial do Streamlit e de exposição executiva |

## Política de Minimização

- IDs diretos ou transacionais não devem ser expostos na camada publicada sem pseudonimização.
- Cidade e prefixo de CEP não devem ser publicados no dashboard quando UF resolve a pergunta de negócio.
- O dashboard deve priorizar agregações por categoria, período, UF, pagamento e status.
- Drill-down detalhado deve usar apenas chaves pseudonimizadas e não dados de localização fina.

## Política de Retenção e Descarte

| Ativo | Política |
| --- | --- |
| `raw/landing` | mantido enquanto necessário para reproduzir o case |
| `standardized` | regenerável; pode ser descartado e recriado |
| `staging` | regenerável; pode ser descartado e recriado |
| `curated/analytics` | mantido como camada interna do pipeline |
| `published/dashboard` | regenerável; publicar apenas a versão vigente do dashboard |
| `screenshots/query_results` | mantidos por fazerem parte da documentação do case |

## Rastreabilidade e Accountability

- toda transformação principal possui script versionado em `src/`
- a coleção local em `data/curated/catalog/` registra os ativos do case
- a qualidade da camada analítica é registrada em `docs/data_quality_report.md`
- a política de publicação segura é registrada em `docs/privacy_governance.md`
- contratos simples de schema validam estrutura mínima em `standardized`, `curated` e `published`

## Limitações

- este projeto não implementa autenticação, RBAC ou catálogo externo real
- os controles aqui documentados representam uma implementação local de governança por design adequada ao escopo do case


