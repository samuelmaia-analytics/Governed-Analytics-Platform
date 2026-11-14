# Resumo profissional e técnico | Professional and technical overview

## Português

Sou Samuel Maia, **Engenheiro de Dados Pleno na Avanade** desde outubro de 2026. Trabalho com engenharia e confiabilidade de dados, combinando Python, SQL, modelagem, testes, governança e automação. Em projetos pessoais independentes da minha atuação corporativa, desenvolvo soluções que tornam decisões sobre dados mais explícitas, verificáveis e fáceis de explicar a áreas técnicas e de negócio.

### Projetos principais

**[Governed Analytics Platform](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform).** Dados sem critérios claros de qualidade e publicação dificultam auditoria e consumo confiável. Construí uma plataforma demonstrativa em Python, SQL, dbt e DuckDB com contratos YAML, Data Quality, lineage, avaliação de risco de privacidade, camadas Bronze/Silver/Gold/Quarantine e Publication Gate com decisões de aprovação, revisão ou bloqueio. O Streamlit foi modernizado em 14/11/2026 com visão executiva e navegação organizada; os endpoints sensíveis do FastAPI exigem token Bearer, compartilhado e sem RBAC/ABAC. A validação local de 13/11/2026 registrou **1.353 testes aprovados, 92% de cobertura em `src + app` e nenhuma falha**. Integrações opcionais e arquiteturas de referência não devem ser confundidas com infraestrutura corporativa implantada.

**[Azure Databricks Governed Lakehouse](https://github.com/samuelmaia-analytics/azure-databricks-governed-lakehouse).** Para preservar consistência de pedidos e produtos, desenvolvi um Lakehouse em Python, PySpark e Delta Lake com camadas analíticas, reconciliação e controles de publicação. A execução local documentou **seis datasets Silver, quatro tabelas Gold e 186 testes**. Azure Databricks é plataforma-alvo; não há evidência de implantação em nuvem concluída.

**[Central de Automação e Operações](https://github.com/samuelmaia-analytics/central-automacao-operacoes).** Para facilitar o acompanhamento de workflows, desenvolvi uma aplicação em Python, SQL, DuckDB e Streamlit integrada ao Pipefy via API/GraphQL, reunindo SLA, backlog, alertas e criticidade. Há modo demonstrativo para ambientes sem credenciais; não há ganhos percentuais declarados sem medição.

[Portfólio](https://samuelmaia-analytics.github.io/samuelmaia-analytics/) · [Demonstração do GAP](https://governed-analytics-platform.streamlit.app/)

## English

I am Samuel Maia, a **mid-level Data Engineer at Avanade** since October 2026. My work focuses on data reliability through Python, SQL, modeling, automated testing, governance and integration. The projects below are personal initiatives and do not represent Avanade or client implementations.

**[Governed Analytics Platform](https://github.com/samuelmaia-analytics/Governed-Analytics-Platform).** To address untrusted analytical publishing, I implemented a Python, SQL, dbt and DuckDB demonstration platform with YAML contracts, quality checks, lineage, privacy risk scoring and an explicit publication gate. Its Streamlit executive interface was redesigned in November 2026; sensitive FastAPI endpoints require a shared Bearer token, without granular authorization. A **13 November 2026 local run passed 1,353 tests with 92% coverage of `src + app`** and no failures. Cloud architecture remains a reference design, not a proven corporate deployment.

**[Azure Databricks Governed Lakehouse](https://github.com/samuelmaia-analytics/azure-databricks-governed-lakehouse).** A PySpark/Delta Lake analytical pipeline with quality controls and reconciliations. Documented local results: **six Silver datasets, four Gold tables and 186 tests**. Cloud deployment is not claimed.

**[Automation & Operations Center](https://github.com/samuelmaia-analytics/central-automacao-operacoes).** A Streamlit, Python, SQL and DuckDB operations hub integrating Pipefy through API/GraphQL for SLA, backlog, alerts and criticality visibility, with sample-data mode when needed.

[Portfolio](https://samuelmaia-analytics.github.io/samuelmaia-analytics/) · [GAP live demo](https://governed-analytics-platform.streamlit.app/)
