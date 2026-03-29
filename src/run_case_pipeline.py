from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.build_analytics import run_build
from src.catalog import main as catalog_main
from src.config import DOCS_DIR, OPS_DIR
from src.data_classification import main as classification_main
from src.export_power_bi import run_export
from src.export_query_result_images import export_all_query_result_images
from src.ingest import configure_logging, run_inventory
from src.preprocess import run_profiling
from src.publish_dashboard import run_publish_dashboard
from src.published_monitoring import (
    run_monitoring,
)
from src.published_monitoring import (
    save_report as save_published_monitoring_report,
)
from src.published_monitoring import (
    save_results as save_published_monitoring_results,
)
from src.quality import (
    load_fact_table,
    run_quality_checks,
    save_quality_report,
    save_quality_results,
)
from src.run_analytics_queries import run_queries, save_execution_manifest
from src.schema_contracts import main as schema_contracts_main
from src.semantic_layer import run_semantic_layer
from src.utils import ensure_directory

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineStep:
    name: str
    description: str


@dataclass(frozen=True)
class StepExecution:
    name: str
    status: str
    duration_seconds: float
    error_message: str = ""


PIPELINE_STEPS = [
    PipelineStep("inventory", "Valida os CSVs de origem e gera o inventário bruto."),
    PipelineStep("profiling", "Promove a camada standardized e gera o profiling exploratório."),
    PipelineStep("build", "Constrói a tabela analítica principal fact_orders_enriched."),
    PipelineStep("publish", "Publica a camada minimizada para consumo do dashboard."),
    PipelineStep("semantic", "Materializa marts semânticos publicados para logística, seller e cohort."),
    PipelineStep("classify", "Materializa o inventário de classificação de dados do projeto."),
    PipelineStep("contracts", "Valida os contratos simples de schema das camadas principais."),
    PipelineStep("quality", "Executa os checks de qualidade e salva os relatórios."),
    PipelineStep("monitor", "Monitora freshness e qualidade da camada publicada."),
    PipelineStep("catalog", "Materializa a coleção local e o inventário catalogável."),
    PipelineStep("queries", "Executa as queries SQL e exporta os resultados tabulares."),
    PipelineStep("screenshots", "Converte os resultados das queries em imagens PNG."),
    PipelineStep("bi", "Exporta os datasets auxiliares para Power BI."),
]
PIPELINE_RESULTS_PATH = OPS_DIR / "operational_job_results.json"
PIPELINE_REPORT_PATH = DOCS_DIR / "operational_job_report.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runner único do case técnico Olist.")
    parser.add_argument(
        "--steps",
        nargs="*",
        choices=[step.name for step in PIPELINE_STEPS],
        help="Lista opcional de etapas para executar. Se omitido, executa o pipeline completo.",
    )
    parser.add_argument(
        "--list-steps",
        action="store_true",
        help="Lista as etapas disponíveis e encerra.",
    )
    return parser.parse_args()


def list_steps() -> None:
    for step in PIPELINE_STEPS:
        print(f"- {step.name}: {step.description}")


def resolve_steps(selected_steps: list[str] | None) -> list[str]:
    if not selected_steps:
        return [step.name for step in PIPELINE_STEPS]
    return selected_steps


def execute_step(step_name: str) -> None:
    if step_name == "inventory":
        run_inventory()
    elif step_name == "profiling":
        run_profiling()
    elif step_name == "build":
        run_build()
    elif step_name == "quality":
        fact_df = load_fact_table()
        results = run_quality_checks(fact_df)
        save_quality_results(results)
        save_quality_report(fact_df, results)
    elif step_name == "publish":
        run_publish_dashboard()
    elif step_name == "semantic":
        run_semantic_layer()
    elif step_name == "classify":
        classification_main()
    elif step_name == "contracts":
        schema_contracts_main()
    elif step_name == "monitor":
        results = run_monitoring()
        save_published_monitoring_results(results)
        save_published_monitoring_report(results)
    elif step_name == "catalog":
        catalog_main()
    elif step_name == "queries":
        results = run_queries()
        save_execution_manifest(results)
    elif step_name == "screenshots":
        export_all_query_result_images()
    elif step_name == "bi":
        run_export()
    else:  # pragma: no cover - defensive branch
        raise ValueError(f"Etapa desconhecida: {step_name}")


def save_pipeline_execution_report(selected_steps: list[str], executions: list[StepExecution]) -> tuple[Path, Path]:
    ensure_directory(OPS_DIR)
    ensure_directory(DOCS_DIR)
    PIPELINE_RESULTS_PATH.write_text(
        json.dumps(
            {
                "selected_steps": selected_steps,
                "executions": [asdict(execution) for execution in executions],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    lines = [
        "# Relatorio Operacional do Job",
        "",
        f"- Etapas solicitadas: `{', '.join(selected_steps)}`",
        f"- Etapas executadas: **{len(executions)}**",
        "",
        "| Etapa | Status | Duracao (s) | Erro |",
        "| --- | --- | ---: | --- |",
    ]
    for execution in executions:
        lines.append(
            f"| `{execution.name}` | **{execution.status}** | {execution.duration_seconds:.2f} | {execution.error_message or '-'} |"
        )
    PIPELINE_REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return PIPELINE_RESULTS_PATH, PIPELINE_REPORT_PATH


def run_selected_steps(selected_steps: list[str]) -> list[StepExecution]:
    executions: list[StepExecution] = []
    for step_name in selected_steps:
        started_at = perf_counter()
        LOGGER.info("Iniciando etapa: %s", step_name)
        try:
            execute_step(step_name)
        except Exception as exc:
            elapsed = perf_counter() - started_at
            executions.append(
                StepExecution(
                    name=step_name,
                    status="FAIL",
                    duration_seconds=elapsed,
                    error_message=str(exc),
                )
            )
            LOGGER.exception("Etapa falhou: %s | duração=%.2fs", step_name, elapsed)
            save_pipeline_execution_report(selected_steps, executions)
            raise
        elapsed = perf_counter() - started_at
        executions.append(StepExecution(name=step_name, status="PASS", duration_seconds=elapsed))
        LOGGER.info("Etapa concluída: %s | duração=%.2fs", step_name, elapsed)
    return executions


def main() -> None:
    args = parse_args()
    if args.list_steps:
        list_steps()
        return

    configure_logging()
    selected_steps = resolve_steps(args.steps)
    LOGGER.info("Pipeline selecionado: %s", ", ".join(selected_steps))
    executions = run_selected_steps(selected_steps)
    save_pipeline_execution_report(selected_steps, executions)


if __name__ == "__main__":
    main()
