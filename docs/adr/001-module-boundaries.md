# ADR 001 — Fronteiras de Módulos (Data Platform, Governed RAG, Governed Extraction)

Status: Proposed

Data: 2026-11-12

## Contexto

A Governed Analytics Platform opera como um monorrepositório com o código principal em `src/`, consumido por:

- UI Streamlit (`app/`).
- API FastAPI (`src/api.py`).
- CLIs e scripts (`python -m src.<módulo>`).
- Testes (`tests/`) que importam diretamente `src.*`.

A ETAPA 0 estabilizou e validou a baseline (Python 3.11.18, 1.111 testes aprovados, cobertura 92%) e normalizou o lockfile (`uv.lock`).

Este documento define fronteiras e contratos de interface para a ETAPA 1 / CHECKPOINT 1, sem implementar refatorações.

## Problema arquitetural

Existe acoplamento relevante entre superfícies (UI/API/CLI/Testes) e o núcleo `src/`, além de dependências do layout físico do repositório. Isso aumenta o risco de regressão ao modularizar.

O objetivo deste checkpoint é inventariar interfaces públicas reais (de fato) e formalizar limites entre domínios antes de qualquer mudança estrutural.

## Evidências do código (inventário de interfaces)

### UI Streamlit (consumidores diretos de `src.*`)

Consumidores principais:

- `app/context.py` importa funções de dados/qualidade/privacidade.
- `app/pages/governance_assistant.py` importa o motor de RAG governado.
- `app/pages/genai_insights.py` referencia o entrypoint `python -m src.genai_feature_extraction --mode reference`.

Módulos `src.*` consumidos pela UI (inventário estático):

- `src.data_loader`, `src.data_quality`, `src.lgpd_classifier`, `src.risk_scoring`, `src.report_generator`
- `src.governance_rag`, `src.publication_gate`, `src.schema_contracts`
- `src.snowflake_connector`, `src.duckdb_engine`, `src.config`, `src.governance_types`, `src.governance_history`

Interfaces públicas (exemplos consumidos pela UI):

- `src.data_loader`: `DEFAULT_SAMPLE_DATASET`, `load_dataset()`.
- `src.data_quality`: `run_data_quality_checks()`, `generate_data_quality_table()`.
- `src.lgpd_classifier`: `classify_dataframe_columns()`.
- `src.risk_scoring`: `calculate_privacy_risk_score()`.
- `src.report_generator`: `generate_markdown_reports()`.
- `src.governance_rag`: `load_corpus()`, `answer_question()`, `LocalIndex`, `RagError`, `MAX_QUESTION_CHARS`.

### API FastAPI

Arquivo: `src/api.py`.

Rotas públicas identificadas:

- `GET /health`
- `GET /api/v1/governance/status`
- `GET /api/v1/snowflake/health`
- `GET /api/v1/snowflake/tables`
- `POST /api/v1/snowflake/query`

Dependências principais:

- Leitura de artefatos locais em `data/published/monitoring/` via `src.config`.
- Integração com conector Snowflake via `src.snowflake_connector`.

### CLIs / scripts

Entrypoints com `argparse.ArgumentParser` e guard `if __name__ == "__main__"`:

- `src/run_platform_pipeline.py`
- `src/governance_rag.py`
- `src/genai_feature_extraction.py`
- `src/published_monitoring.py`
- `src/platform_publication.py`
- `src/governance_validation.py`
- `src/release_management.py`
- `src/workflow_policy_validation.py`
- `src/dadosfera_api_key.py`, `src/dadosfera_catalog_sync.py`, `src/dadosfera_pipeline_ops.py`

### Testes

Os testes importam diretamente uma superfície ampla de `src.*`. Na prática, a suíte funciona como um contrato de compatibilidade para imports e comportamento.

### Dependências de layout físico (root e paths)

Padrões identificados:

- Múltiplos módulos suportam execução como script via `sys.path.append(str(Path(__file__).resolve().parent.parent))`.
- `src/governance_rag.py` define `PROJECT_ROOT = Path(__file__).resolve().parent.parent` e `MANIFEST_PATH = PROJECT_ROOT / "config/governance_rag_sources.yml"`.
- `src/config.py` suporta `PROJECT_ROOT_DIR` (env var) com fallback para `Path(__file__).resolve().parent.parent`.

Implicação: movimentações físicas de arquivos tendem a quebrar CLIs e UI se a resolução de root não for estabilizada.
## Domínios e responsabilidades

### Data Platform

Responsabilidades:

- Ingestão, processamento, transformações e pipelines.
- Contratos e qualidade (ex.: schema contracts, regras e outputs).
- Privacidade e governança (classificação LGPD, risk scoring, minimização).
- Publication Gate e publicação da camada minimizada.
- Lineage, observabilidade e monitoramento.
- dbt, SQL e DuckDB; conectores (ex.: Snowflake, Postgres).

Superfícies públicas de fato (não-exaustivo):

- Orquestração/pipeline: `src/run_platform_pipeline.py`.
- API: `src/api.py`.
- Qualidade e publicação: `src/quality.py`, `src/publish_dashboard.py`, `src/published_monitoring.py`, `src/platform_publication.py`.
- Contratos: `src/schema_contracts.py`.
- Gate: `src/publication_gate.py`.

### Governed RAG

Responsabilidades:

- Manifesto de fontes aprovadas (`config/governance_rag_sources.yml`).
- Coleta local de evidências com verificação SHA-256.
- Recuperação determinística local (TF-IDF) e ranking.
- Citações, abstenção e resposta baseada somente em evidência.
- Consentimento explícito e gating para provedor externo.

Superfície pública de fato:

- `src/governance_rag.py`: `load_corpus()`, `LocalIndex.retrieve()`, `answer_question()`, `RagError`.

### Governed Extraction

Responsabilidades:

- Entrada e normalização (CSV de texto/fonte).
- Extração estruturada e validação mínima do payload.
- Proveniência do modo utilizado.
- Modos: `reference` (determinístico) e `openai` (opcional e dependente de credenciais).

Superfície pública de fato:

- `src/genai_feature_extraction.py`: `extract_features()`, `flatten_results()`, `write_jsonl()`, `main()`.

## Dependências permitidas e proibidas (propostas)

Permitidas:

- UI Streamlit e FastAPI podem consumir APIs públicas dos domínios.
- Data Platform pode consumir subcomponentes internos já modularizados (ex.: `*_components/`, `publication_shadow/`, `publication_provenance/`).

Proibidas (diretrizes):

- Governed RAG não deve depender do runtime de pipeline (ex.: não importar `run_platform_pipeline` nem executar steps de processamento).
- Governed Extraction não deve depender da execução do pipeline; opera por inputs/artefatos bem definidos.
- UI/API não devem tomar decisão de publicação lendo contratos YAML diretamente; a decisão é responsabilidade do Publication Gate.

## Alternativas consideradas

- Manter a estrutura atual sem fronteiras explícitas: rejeitada (aumenta risco e custo de evolução).
- Mover arquivos imediatamente para novos subpacotes: rejeitada no CHECKPOINT 1 (alto risco de quebra por dependências de paths e imports).
- Criar facades/wrappers já no CHECKPOINT 1: adiado (primeiro inventariar e acordar contratos de interface).
- Dividir em múltiplos repositórios: rejeitada no curto prazo (custo operacional e risco de regressão).

## Decisões propostas (não implementadas)

- Formalizar três domínios: Data Platform, Governed RAG, Governed Extraction.
- Tratar UI Streamlit, FastAPI, CLIs e testes como consumidores que definem a API pública de fato.
- Executar modularização de forma incremental, priorizando compatibilidade retroativa de imports e entrypoints.

## Consequências

- Redução de risco em refatorações futuras (mudanças menores e verificáveis).
- Necessidade de disciplina explícita de dependências entre domínios.

## Compatibilidade retroativa

- Preservar imports atuais (`from src.<módulo> import ...`) durante a transição.
- Preservar execução `python -m src.<módulo>` para CLIs existentes.
- Preservar o comportamento determinístico do Governed RAG e do modo `reference` da extração.

## Riscos e limitações

### Divergência entre contratos YAML e enforcement runtime (Publication Gate)

Risco arquitetural: contratos YAML descrevem políticas/limiares de publicação por dataset, enquanto o enforcement no runtime pode estar codificado/centralizado.

Evidência:

- Contratos: presença de `publication_policy`/`publication_criteria` (ex.: `contracts/customer_privacy_contract.yml`, `contracts/published/fact_orders_dashboard.contract.yml`).
- Runtime: decisão e thresholds em `src/publication_gate.py`.

Atividade recomendada (separada): "Policy Enforcement Alignment"

- Definir formalmente a fonte da verdade (contrato vs defaults do código).
- Instrumentar e testar conformidade (contrato aplicado vs decisão gerada).
- Decidir se thresholds serão parametrizáveis por contrato/dataset ou se os contratos devem refletir explicitamente política global.

### Dependência de layout físico

- Uso disseminado de `Path(__file__)` e `sys.path.append(...)` aumenta risco de regressão ao mover módulos.

## Critérios objetivos de aceitação (CHECKPOINT 1)

- ADR criada com `Status: Proposed`.
- Interfaces públicas inventariadas com evidência (UI/API/CLI/tests).
- Domínios e dependências permitidas/proibidas definidos.
- Sem mudanças em código de negócio, imports existentes, dependências ou comportamento determinístico.
