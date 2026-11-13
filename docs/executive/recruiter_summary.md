# Resumo profissional (Método IEO) / Recruiter Summary (IEO Method)

## PT-BR — resumo (60–100 palavras)

Sou Samuel Maia, Engenheiro de Dados Pleno na Avanade. Trabalho no desenvolvimento de pipelines e produtos analíticos com foco em confiabilidade: contratos de dados, qualidade automatizada, lineage e critérios explícitos de publicação. Em projetos pessoais de portfólio, aplico o mesmo rigor para produzir evidências auditáveis (testes, cobertura e artefatos) e deixar claros os limites entre demonstração e implantação corporativa, sem associar esses projetos ao meu vínculo profissional.

## EN — 60–100 word summary

I’m Samuel Maia, a Mid-level Data Engineer at Avanade. I build data pipelines and analytics products with a reliability-first approach: data contracts, automated quality checks, lineage, and explicit publication criteria. In my personal portfolio projects, I apply the same discipline to produce auditable evidence (tests, coverage, and artifacts) while keeping a clear boundary between demos and corporate-grade deployments, and without implying employer endorsement.

---

## PT-BR — detalhes

### Problemas que eu resolvo

- Publicação de dados sem critérios claros de qualidade/privacidade, que gera inconsistência e dificulta auditoria.
- Falta de fronteira entre camada técnica (curated) e camada de consumo (published), que aumenta risco e retrabalho.
- Baixa visibilidade operacional de processos e workflows (SLA, backlog, criticidade e alertas).

### Projetos principais (CAR)

#### 1) Governed Analytics Platform (portfólio)

- Contexto: dados analíticos sem contratos, qualidade e critérios de publicação tendem a gerar inconsistências e dificultam consumo confiável.
- Ação: plataforma demonstrativa com camadas Bronze/Silver/Gold e Quarantine; Data Contracts, Data Quality, Lineage e Publication Gate com estados explícitos (aprovação, revisão e bloqueio). Inclui Streamlit, FastAPI, observabilidade e controles inspirados na LGPD.
- Resultado (verificado no repositório): suíte global com **1.353 testes aprovados**, **92% de cobertura** (escopo `src` + `app`) em execução local de **13/11/2026**. A API FastAPI exige **autenticação Bearer** em quatro endpoints sensíveis (token compartilhado, sem RBAC/ABAC).

Links:

- Repositório: https://github.com/samuelmaia-analytics/Governed-Analytics-Platform
- Demo Streamlit: https://governed-analytics-platform.streamlit.app/

Limites:

- Projeto de portfólio (não declarar produção corporativa).
- Autenticação por token compartilhado, sem autorização granular (RBAC/ABAC).

Implementado x Simulado (transparência):

- Implementado: pipeline local, contratos, qualidade, gate de publicação, app Streamlit, API FastAPI e evidências no repositório.
- Simulado/demonstrativo: metadados legais (controller/operator/DPO) com valores fictícios e materiais de RIPD em escopo de portfólio.

#### 2) Azure Databricks Governed Lakehouse (portfólio)

- Contexto: pipelines analíticos precisam garantir integridade, qualidade e consistência antes da publicação para consumo.
- Ação: lakehouse com Python, PySpark e Delta Lake, camadas Bronze/Silver/Gold e Quarantine, schemas explícitos e Publication Gate.
- Resultado (documentado no currículo/repositório): **6 datasets Silver publicados** em execução local, **4 tabelas Gold**, reconciliações sem perda ou multiplicação de registros e **186 testes automatizados**.

Link:

- Repositório: https://github.com/samuelmaia-analytics/azure-databricks-governed-lakehouse

Limite: Azure Databricks é plataforma-alvo; não declarar implantação em nuvem concluída sem evidência.

#### 3) Central de Automação e Operações (portfólio)

- Contexto: acompanhar múltiplos workflows exige visibilidade de prazos, responsáveis, backlog e criticidade operacional.
- Ação: central com Python, SQL, DuckDB e Streamlit, integrando Pipefy via API/GraphQL.
- Resultado: visão consolidada de SLA, backlog, alertas, regras de criticidade e identificação de demandas vencidas/sem responsável (sem atribuir percentuais sem evidência).

Link:

- Repositório: https://github.com/samuelmaia-analytics/central-automacao-operacoes

### Pontos de conversa técnica (entrevista)

1. Por que separar camadas curated vs published reduz risco e facilita governança.
2. Como contratos e checks de qualidade viram evidência antes da publicação.
3. Como critérios de privacidade podem ser modelados tecnicamente (sem alegar parecer jurídico).
4. Como tornar a API de governança segura por padrão e “fail-closed”.

---

## EN — detailed version

### Problems I solve

- Publishing analytics data without clear quality/privacy criteria, which creates inconsistency and complicates audits.
- Missing separation between curated engineering layers and published consumption layers.
- Low operational visibility across workflows (SLA, backlog, ownership, and alerting).

### Featured projects (CAR)

#### 1) Governed Analytics Platform (portfolio)

- Context: analytics data without contracts and governance gates is hard to trust and audit.
- Action: a portfolio platform with Bronze/Silver/Gold and Quarantine layers; Data Contracts, Data Quality, Lineage and a Publication Gate with explicit decision states. Includes Streamlit, FastAPI, observability and LGPD-inspired controls.
- Result (verified in-repo): **1,353 passing tests** and **92% total coverage** (scope `src` + `app`) from a local run on **13 Nov 2026**. The FastAPI surface enforces **Bearer authentication** on four sensitive endpoints (shared token; no RBAC/ABAC).

Links:

- Repo: https://github.com/samuelmaia-analytics/Governed-Analytics-Platform
- Streamlit demo: https://governed-analytics-platform.streamlit.app/

Limitations:

- Portfolio scope (not an enterprise production deployment claim).
- Shared-token authentication only (no fine-grained authorization).

Implemented vs simulated (explicit):

- Implemented: local pipeline, contracts, quality checks, publication gate, Streamlit app, FastAPI API and evidence artifacts.
- Simulated/demo: legal governance metadata (controller/operator/DPO) with fictional values and RIPD sample content.

#### 2) Azure Databricks Governed Lakehouse (portfolio)

- Context: analytics pipelines must preserve integrity and reliability before publishing.
- Action: a lakehouse implementation with Python, PySpark and Delta Lake, Bronze/Silver/Gold and Quarantine, explicit schemas and a Publication Gate.
- Result (as documented in the repo/CV): **6 Silver datasets**, **4 Gold tables**, reconciliations with no record loss or duplication, and **186 automated tests**.

Repo:

- https://github.com/samuelmaia-analytics/azure-databricks-governed-lakehouse

Limitation: Azure Databricks is the target platform; do not claim a completed cloud deployment without evidence.

#### 3) Automation & Operations Center (portfolio)

- Context: managing multiple workflows requires SLA and backlog visibility.
- Action: a Streamlit-based operations center using Python, SQL and DuckDB, integrating with Pipefy via API/GraphQL.
- Result: consolidated view of SLA, backlog, alerts, criticality rules and detection of overdue/unassigned demands (no unverified percentage claims).

Repo:

- https://github.com/samuelmaia-analytics/central-automacao-operacoes

### Technical interview talking points

1. Why curated vs published boundaries reduce risk and improve governance.
2. How contracts and quality checks become publish-time evidence.
3. How privacy criteria can be modeled as engineering controls (not legal advice).
4. How to enforce fail-closed API authentication for governance endpoints.
