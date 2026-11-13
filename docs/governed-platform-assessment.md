# Governed Analytics Platform — Inventário, Diagnóstico Arquitetural e Validação (ETAPA 0)

Data: 2026-11-12

## Escopo e restrições

Objetivo desta etapa:

- Inventariar componentes relevantes da plataforma com base em evidências (código, testes e documentação existente).
- Desbloquear o ambiente Python local e validar a capacidade de executar a suíte de testes com cobertura nesta máquina.

Restrições observadas:

- Sem uso de GitHub MCP, OpenAI API ou serviços pagos.
- Sem alterações em lógica de negócio, contratos, pipelines ou `pyproject.toml`.
- Alteração controlada do `uv.lock` para normalização de reprodutibilidade (delta mínimo para `psycopg[binary]`).
- Execução da suíte Pytest com cobertura apenas para validar a normalização do lockfile (evitar reexecuções desnecessárias).
- Alterações no repositório limitadas a este relatório e ao `uv.lock` (além de diretórios locais do ambiente Python criados durante a sessão).

---

## 0) Resultado executivo (ETAPA 0)

- Ambiente Python funcional via `uv` com Python 3.11.18 e `.venv` no repositório.
- Lockfile normalizado para refletir `psycopg[binary]>=3.2,<4` (adição de `psycopg==3.3.9` e `psycopg-binary==3.3.9` no `uv.lock`), com `uv lock --check` OK e `uv sync --locked --extra dev` OK.
- Testes (pós-normalização do lockfile, 2026-11-12): **1.111 aprovados**, **0 falhas**, **cobertura total 92%**, **duração 102,50s**.
- Baseline anterior (ETAPA 0, antes da normalização do lockfile): **1.111 aprovados**, **0 falhas**, **cobertura total 92%**, **duração 75,94s**.
- Riscos remanescentes prioritários: possível divergência entre política de publicação declarada em contratos YAML e enforcement efetivo no runtime; warning recorrente de line endings (LF→CRLF) no Windows para `uv.lock`.

## 0.1) Integridade do repositório (Git)

Diagnóstico real (capturado durante esta consolidação):

- `git status --porcelain=v1 --untracked-files=all` → `M uv.lock` e `?? docs/governed-platform-assessment.md`.
- `git diff --name-status` → `M uv.lock`.

Nota sobre `git restore` (sem execução nesta consolidação):

- Durante a preparação do ambiente, foi utilizado `git restore` para reverter tentativas do `uv` de modificar arquivos rastreados.
- **Não é possível comprovar retroativamente**, apenas com o estado atual, se havia alterações locais preexistentes do usuário no momento do `git restore`.
  - Evidência observável hoje: o repositório está limpo para arquivos rastreados.
  - Risco residual: se existiam alterações locais não commitadas em arquivos rastreados na ocasião, elas poderiam ter sido descartadas.

## 0.2) Normalização controlada do lockfile (pré-ETAPA 1)

Evidências reais (capturadas nesta sessão):

- `uv --version` → `uv 0.13.7 (316c827e0 2026-11-03 x86_64-pc-windows-msvc)`.
- Python efetivo: `CPython 3.11.18` via `.venv` em `./.venv/Scripts/python.exe`.
- Diretórios locais (somente sessão): `UV_CACHE_DIR=./.uv-cache` e `UV_PYTHON_INSTALL_DIR=./.uv-python`.
- Divergência detectada: `pyproject.toml` declara `psycopg[binary]>=3.2,<4`, mas o `uv.lock` anterior não materializava `psycopg`/`psycopg-binary`, fazendo `uv lock --check` falhar.
- Diagnóstico: `uv lock --dry-run --managed-python -p 3.11.18` → `Add psycopg v3.3.9` e `Add psycopg-binary v3.3.9`.
- Aplicação (sem `--upgrade`): `uv lock --managed-python -p 3.11.18` → adicionou `psycopg==3.3.9` e `psycopg-binary==3.3.9` ao `uv.lock`.
- Validação: `uv lock --check --managed-python -p 3.11.18` → OK.
- Sincronização: `uv sync --locked --extra dev --managed-python -p 3.11.18` → OK (recriou `.venv`).
- Regressão: `python -m pytest --cov=src --cov=app --cov-report=term` → `1111 passed`, cobertura total `92%`, duração `102,50s`.

---

## 1) Estrutura do repositório (alto nível)

Pastas relevantes identificadas

- `src/`: núcleo Python da plataforma (pipeline, governança, qualidade, privacidade, publicação, RAG, observabilidade, API).
- `app/`: aplicação Streamlit (UI e páginas).
- `contracts/`: contratos YAML (camadas e artefatos de governança).
- `tests/`: suíte Pytest.
- `dbt/`: projeto dbt.
- `.github/workflows/`: pipelines CI/CD.
- `workflows/n8n/`: templates de automação n8n.

Arquivos-chave verificados (existência)

- Publication gate: `src/publication_gate.py`
- Orquestração/pipeline: `src/run_platform_pipeline.py`
- Histórico/auditoria: `src/governance_history.py`
- Governed RAG (local): `src/governance_rag.py`
- Extração estruturada (referência/OpenAI opcional): `src/genai_feature_extraction.py`
- Streamlit UI: `app/main.py` e `app/pages/governance_assistant.py`
- FastAPI: `src/api.py`
- CI: `.github/workflows/ci.yml`
- dbt: `dbt/dbt_project.yml` e `dbt/profiles.yml`
- DuckDB engine: `src/duckdb_engine.py`
- n8n: `workflows/n8n/governed_analytics_pipeline.json`

---

## 2) Visão arquitetural (recuperada e consolidada)

Referência arquitetural detalhada já existente no repositório:

- `docs/architecture/architecture.md` (visão lógica, fluxo de dados/governança, responsabilidades, limites de “production-inspired”).

Componentes e fluxos (síntese baseada na documentação + evidências em código)

- Ingestão/carregamento → profiling/EDA → classificação LGPD → regras de qualidade → risk scoring → validação de contratos → camada publicada → scorecards → histórico/monitoramento → consumo em Streamlit/API.
- Separação explícita entre processamento analítico interno e consumo publicado (camada publicada e artefatos governados).

### 2.1) Inventário com classificação por evidência

Definições:

- **Implementado**: existe implementação no código.
- **Testado**: há testes explícitos (ou evidência forte por testes/dedicação na suíte).
- **Parcial**: existe implementação, mas integração/enforcement não é completo em todos os fluxos.
- **Proposto**: existe apenas como documentação/arquitetura de referência.
- **Pendente**: documentação declara intenção, mas não há evidência de implementação.

| Componente | Evidência principal | Classificação | Observações |
| --- | --- | --- | --- |
| Pipeline e orquestração (Python) | `src/run_platform_pipeline.py`, `scripts/run_governance_pipeline.py` | Implementado; testado (suíte global) | Múltiplos entrypoints (Python, scripts e camada dbt). |
| Contratos de dados (YAML) | `docs/data_contracts.md`, pasta `contracts/` | Implementado; parcial | Contratos declaram políticas de publicação; enforcement runtime precisa ser confirmado (risco). |
| Publication Gate | `src/publication_gate.py`, `docs/publication_gate.md`, `tests/test_publication_gate.py` | Implementado; testado | Há testes dedicados e testes de integração com governança/pipeline. |
| Governança/histórico | `src/governance_history.py` | Implementado; testado (suíte global) | Evidência de `run_id` e trilhas em múltiplos módulos. |
| Lineage | `src/lineage.py`, `docs/data_lineage.md` | Implementado; parcial | Linhagem bem documentada; validação por execução real do pipeline está fora do escopo desta etapa. |
| Streamlit (camada executiva) | `app/main.py`, `app/pages/*` | Implementado; testado (suíte global) | Páginas e componentes possuem testes de renderização/contratos. |
| Governed RAG local | `src/governance_rag.py`, `docs/governance_rag.md`, `tests/test_governance_rag.py` | Implementado; testado | TF‑IDF, validação por manifesto, SHA‑256, citações e abstenção. |
| OpenAI opcional (extração/integração) | `src/genai_feature_extraction.py`, `app/pages/governance_assistant.py` | Implementado; testado (parcial) | Condicionado a consentimento/flags; não utilizado nesta etapa. |
| FastAPI (API de governança) | `src/api.py`, `tests/test_api.py`, dependência no `pyproject.toml` | Implementado; testado | Endpoints expõem status/governança. |
| dbt + DuckDB (SQL modeling) | `dbt/*`, `pyproject.toml` (`dbt-duckdb`), `docs/architecture/architecture.md` | Implementado; parcial | Documentação indica que dbt não é invocado automaticamente por `src/run_platform_pipeline.py`. |
| DuckDB (camada analítica local) | `src/duckdb_engine.py`, `src/build_analytics.py`, `tests/test_duckdb_engine.py` | Implementado; testado | Persistência em DuckDB e helpers testados. |
| n8n (automação/orquestração) | `workflows/n8n/*`, `docs/n8n_automation.md`, `tests/test_n8n_automation_page.py` | Implementado; parcial | Workflows são templates; alertas (Discord) são placeholders e requerem configuração no n8n. |
| Observabilidade / logs / telemetry | `src/observability.py`, `src/governance_observability.py`, `docs/operational_logs.md` | Implementado; testado (suíte global) | Trilhas por `run_id`, artefatos de observabilidade e logs simulados/estruturados. |
| CI/CD | `.github/workflows/ci.yml` | Implementado | Lint, mypy (subset), smoke checks e pytest com cobertura. |
| Arquiteturas cloud (AWS/Azure) | `docs/aws/*`, `docs/architecture/*` | Proposto | Referência/planejamento; sem evidência de deployment real nesta etapa. |

---

## 3) Evidências de implementação relevantes (pontos exigidos)

### 3.1 Contratos YAML e políticas de publicação

Evidência (existência nos contratos):

- Diversos contratos em `contracts/` contêm `publication_policy`, `blocking_conditions` e `publication_criteria`.
  - Exemplos observáveis: `contracts/published/fact_orders_dashboard.contract.yml`, `contracts/curated/fact_orders_enriched.contract.yml`.

Risco arquitetural obrigatório:

- A busca por `publication_policy`, `blocking_conditions` e `publication_criteria` não retornou ocorrências em `src/`.
  - Isso sugere que as regras declaradas podem estar sendo aplicadas via outra camada/transformação (ou manualmente), ou que não há enforcement runtime direto desses campos.

Conclusão (sem extrapolar):

- Há evidência de políticas declaradas nos contratos.
- A aplicação efetiva dessas políticas no runtime não está comprovada apenas por ligação direta visível entre os contratos e a lógica em `src/`.

### 3.2 Publication Gate

- Implementação determinística em `src/publication_gate.py`.
- Documentação em `docs/publication_gate.md`.
- Evidência de testes dedicados em `tests/test_publication_gate.py` e testes de pipeline/governança.

### 3.3 Governed RAG (TF‑IDF, SHA‑256, citações, abstenção)

- Implementação em `src/governance_rag.py`:
  - valida manifesto YAML e exige fontes aprovadas;
  - exige SHA‑256; calcula hash com normalização de quebras de linha (LF);
  - recuperação TF‑IDF;
  - resposta com citações; valida correspondência “citação ↔ trecho recuperado”;
  - mecanismo de abstenção quando não há evidência.
- Documentação detalhada em `docs/governance_rag.md` (inclui fontes aprovadas e limites do escopo).

### 3.4 Streamlit + consentimento para OpenAI

- Streamlit: `app/main.py` e páginas em `app/pages/*`.
- Consentimento por consulta e flags de habilitação em `app/pages/governance_assistant.py` (modo local TF‑IDF vs modo OpenAI com aviso de possível cobrança).

### 3.5 FastAPI / APIs

- API em `src/api.py` (FastAPI).
- Dependência `fastapi` declarada em `pyproject.toml`.

### 3.6 dbt + DuckDB

- dbt: `dbt/dbt_project.yml`, `dbt/profiles.yml`, `dbt/README.md`.
- DuckDB engine e persistência: `src/duckdb_engine.py`, `src/build_analytics.py`.

### 3.7 n8n

- Templates importáveis: `workflows/n8n/*`.
- Documentação com limites/placeholder de alertas: `docs/n8n_automation.md`.

### 3.8 Observabilidade

- Logs e interpretação: `docs/operational_logs.md`.
- Componentes: `src/observability.py`, `src/governance_observability.py` e artefatos correlatos.

### 3.9 CI/CD

- Workflow CI: `.github/workflows/ci.yml`.
  - Instala dependências com `uv sync --extra dev`.
  - Executa ruff e mypy (subset).
  - Smoke check do entrypoint do pipeline.
  - Executa pytest com cobertura (`--cov=src --cov=app`).

---

## 4) Ambiente Python — diagnóstico e correção controlada

### 4.1 Diagnóstico inicial (pré-correção)

- `python` no PATH: stub da Microsoft Store (não utilizável para este projeto nesta máquina).
- Requisito do projeto em `pyproject.toml`: `requires-python = ">=3.11,<3.14"`.

### 4.2 Correção aplicada (local, isolada no repositório)

Objetivo: evitar locks/ACL de diretórios globais do `uv` e garantir Python 3.11 compatível.

Configuração aplicada apenas na sessão:

- `UV_CACHE_DIR=./.uv-cache`
- `UV_PYTHON_INSTALL_DIR=./.uv-python`

Python e virtualenv:

- Python instalado via `uv`: **3.11.18**.
- Virtualenv do repositório: `.venv/`.

Ignorados pelo Git (sem alterar `.gitignore`):

- `.venv/` é ignorado por `.gitignore`.
- `coverage.xml`, `.pytest_cache/` e `.coverage` são ignorados por `.gitignore`.

---

## 5) Divergência `pyproject.toml` vs `uv.lock` (impacto em `--locked`)

Evidências registradas durante a correção do ambiente (diagnóstico apenas; sem atualização de lockfile):

- `uv lock --check --managed-python -p 3.11.18` indicou que o lockfile “precisa ser atualizado”.
- `uv lock --dry-run --managed-python -p 3.11.18` indicou (sem aplicar mudanças) necessidade de adicionar:
  - `psycopg v3.3.9`
  - `psycopg-binary v3.3.9`

Evidência adicional (configuração do projeto):

- `pyproject.toml` declara `psycopg[binary]>=3.2,<4`.

Interpretação (sem afirmar causa-raiz definitiva):

- A necessidade de “atualizar” o `uv.lock` pode decorrer de:
  - alteração real de dependências em algum momento anterior;
  - mudança de metadados/normalização do `uv` (p.ex. representação de extras `psycopg[binary]`); e/ou
  - comportamento dependente de versão do `uv`.

Impacto observado:

- `uv sync --locked` ficou bloqueado, exigindo a mitigação temporária `--frozen` para validar o ambiente local.

Nota sobre CI:

- O CI em `.github/workflows/ci.yml` usa `uv sync --extra dev` (sem `--locked`), então a divergência do lockfile pode não bloquear o pipeline atual, mas segue como dívida técnica/risco de reprodutibilidade estrita.

---

## 6) Testes e cobertura (execução real nesta máquina)

Atualização (Checkpoint 16C — 13/11/2026): a suíte global foi reexecutada nesta máquina usando o Python do ambiente virtual do repositório (sem depender do `python` do PATH) e com isolamento de artefatos fora do working tree.

- Testes coletados: **1.353**
- Testes aprovados: **1.353**
- Falhas/erros/skips: **0/0/0**
- Cobertura total: **92%** (escopo: `src` + `app`)

Comando equivalente utilizado (PowerShell, na raiz do projeto):

- `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --cov=src --cov=app --cov-report=term-missing`

Nota: dados de cobertura foram direcionados para diretório temporário externo ao repositório (não gerando `.coverage`, `coverage.xml` ou `htmlcov/` no working tree).


Importante (histórico): na consolidação original desta etapa, os testes não foram reexecutados; veja a atualização do Checkpoint 16C acima.

Comando executado (histórico da validação do ambiente):

- `uv run --managed-python -p 3.11.18 pytest -ra --cov=src --cov=app --cov-report=term-missing --cov-report=xml`

Resultados confirmados:

- Testes coletados: **1.111**
- Aprovados: **1.111**
- Falhos: **0**
- Ignorados/Skipped: **0** (não houve indicação de skips no resumo final do pytest)
- Duração: **75,94s**

Cobertura:

- Cobertura total (global): **92%**
  - TOTAL: 8555 statements
  - 708 missing
- Artefato gerado: `coverage.xml` (ignorado pelo Git)

---

## 7) Riscos e pendências (sem correção nesta etapa)

### Criticidade alta

- Possível divergência entre contratos YAML e enforcement runtime: contratos definem `publication_policy`/`publication_criteria`, mas a ligação direta desses campos com a lógica de runtime não está evidenciada por referência textual no código em `src/`.
  - Risco: policy drift (contrato declara regra, runtime aplica outra ou nenhuma).
  - Recomendação (para etapa posterior, não executada aqui): mapear “contrato → validações → gate → persistência de decisão” e adicionar testes de integração contrato-a-contrato.

### Criticidade média

- Divergência `pyproject.toml` vs `uv.lock`: `uv lock --check` indica necessidade de atualização; `uv lock --dry-run` sugere inclusão de `psycopg` e `psycopg-binary`.
  - Impacto: bloqueia `--locked` e reduz reprodutibilidade estrita.
- Risco de descarte de alterações locais prévias (histórico): `git restore` foi utilizado durante a correção do ambiente para preservar arquivos rastreados; o estado atual está limpo, mas não prova a inexistência de mudanças locais anteriores na ocasião.
- Execução fora do `uv` pode falhar: `python` no PATH aponta para stub da Microsoft Store; executar via `uv run` e o `.venv` do repositório é o caminho confiável.

### Criticidade baixa

- Relatório não rastreado: `docs/governed-platform-assessment.md` está como untracked; decisão de versionar depende do fluxo do repositório.

---

## 8) Critério de conclusão da ETAPA 0

Critérios atendidos nesta máquina:

- [x] Ambiente Python funcional (Python 3.11.18, `.venv` local via `uv`).
- [x] Dependências de desenvolvimento instaladas sem alterar `pyproject.toml`/`uv.lock`.
- [x] Suíte de testes executada com sucesso (1.111/1.111).
- [x] Cobertura registrada (92%).

Pendências para considerar antes/ao iniciar a ETAPA 1 (não executada aqui):

- [~] Analisar/enforçar alinhamento contrato (YAML) ↔ runtime (publication policy).
- [~] Endereçar divergência `uv.lock` vs `pyproject.toml` de forma controlada.

ETAPA 1

- Não executada (requer autorização explícita).
