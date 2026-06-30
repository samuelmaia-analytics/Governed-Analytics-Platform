# Operational Runbook

Este runbook descreve como operar o Governed Analytics Platform em ambiente
local de portfolio, sem credenciais reais e sem alegar producao empresarial.

## Executar Localmente

```bash
python -m venv .venv
.venv/Scripts/activate
uv sync --extra dev
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
uv sync --extra dev
```

Executar o app modular principal:

```bash
uv run streamlit run app/main.py
```

Executar o app raiz de evidencias operacionais:

```bash
uv run streamlit run app.py
```

## Executar O Pipeline

Listar etapas disponiveis:

```bash
uv run python src/run_platform_pipeline.py --list-steps
```

Executar pipeline completo:

```bash
uv run python src/run_platform_pipeline.py
```

Executar apenas etapas especificas:

```bash
uv run python src/run_platform_pipeline.py --steps build publish semantic quality monitor
```

## Validar Logs

Logs controlados de exemplo ficam em `logs/`:

- `logs/pipeline_execution_logs.csv`
- `logs/data_quality_logs.csv`
- `logs/lgpd_classification_logs.csv`
- `logs/publication_gate_logs.csv`
- `logs/error_logs.csv`

Validacao rapida:

```bash
uv run python -c "import pandas as pd; [print(path, pd.read_csv(path).shape) for path in ['logs/pipeline_execution_logs.csv','logs/data_quality_logs.csv','logs/lgpd_classification_logs.csv','logs/publication_gate_logs.csv','logs/error_logs.csv']]"
```

## Se Data Quality Falhar

1. Abrir `logs/data_quality_logs.csv` e identificar checks com `FAIL` ou `WARN`.
2. Verificar severidade, linhas afetadas e descricao da regra.
3. Revisar regras em `contracts/data_quality_rules.yml`.
4. Corrigir a origem ou a transformacao responsavel.
5. Reexecutar a etapa de qualidade:

```bash
uv run python src/run_platform_pipeline.py --steps quality
```

## Se LGPD Risk For Alto

1. Abrir `logs/lgpd_classification_logs.csv`.
2. Identificar colunas com `risk_level` alto ou recomendacao restritiva.
3. Revisar regras em `contracts/governance/lgpd_classification_rules.yml`.
4. Aplicar mascaramento, pseudonimizacao, agregacao ou remocao conforme o caso.
5. Reexecutar classificacao e score de risco.

## Se Publication Gate Bloquear Dados

1. Abrir `data/gold/publication_decisions.csv`.
2. Confirmar se a decisao foi `Blocked`.
3. Ler o campo `reason`.
4. Investigar se o bloqueio veio de qualidade, risco LGPD ou issues criticas.
5. Corrigir a causa raiz antes de qualquer nova publicacao.
6. Reexecutar o gate:

```bash
uv run python scripts/run_publication_gate.py --dataset-name fact_orders_dashboard --quality-score 92 --lgpd-risk-score 45 --critical-issues 0
```

## Reprocessar Uma Execucao

1. Registrar o contexto da falha no log operacional.
2. Corrigir dados, contratos ou transformacoes.
3. Reexecutar apenas as etapas necessarias quando possivel.
4. Rodar testes antes de considerar a entrega pronta:

```bash
uv run pytest
uv run ruff check src app tests scripts
```

## Investigar Erro

1. Abrir `logs/error_logs.csv`.
2. Filtrar por `execution_id` e `step_name`.
3. Ler `error_type`, `error_message`, `severity` e `recommended_action`.
4. Comparar com o relatorio operacional em `docs/reports/operational_job_report.md`, quando disponivel.
5. Reproduzir localmente com a menor etapa possivel.

## Checklist Antes De Apresentar O Projeto

- `git status` sem alteracoes inesperadas.
- `uv run pytest` passando.
- `uv run ruff check src app tests scripts` passando.
- Streamlit abre com `uv run streamlit run app/main.py`.
- README atualizado com os documentos principais.
- Logs de exemplo sem dados sensiveis reais.
- Publication Gate com exemplos `Approved`, `Needs Review` e `Blocked`.
- Explicar claramente o que e implementado, simulado e referencia de arquitetura.
