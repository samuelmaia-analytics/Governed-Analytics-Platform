from __future__ import annotations

import argparse
import json
import logging
import platform
import subprocess
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Callable, Iterator

import pandas as pd

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.build_analytics import run_build
from src.business_rule_validation import main as business_rules_main
from src.catalog import main as catalog_main
from src.config import DOCS_DIR, OPS_DIR, PATHS
from src.data_classification import main as classification_main
from src.export_power_bi import run_export
from src.export_query_result_images import export_all_query_result_images
from src.governance_history import save_publication_decision_artifact
from src.governance_observability import (
    evaluate_governance_observability,
    load_governance_history,
    save_observability_results,
)
from src.governance_scorecards import main as governance_scorecards_main
from src.ingest import configure_logging, run_inventory
from src.lineage import main as lineage_main
from src.monitoring_components.models import MonitoringCheckResult
from src.observability_components.models import ObservabilityCheck
from src.preprocess import run_profiling
from src.publication_provenance import (
    DEFAULT_DATASET_CONTENT_PROVENANCE_PATH,
    SHADOW_REQUIRED_SOURCES,
    PipelineGovernanceContext,
    append_dataset_content_provenance,
    build_dataset_content_provenance,
    validate_evidence_provenance,
)
from src.publication_shadow import (
    DEFAULT_DUAL_PRIVACY_TELEMETRY_PATH,
    DEFAULT_SHADOW_TELEMETRY_PATH,
    CurrentMonitorDecision,
    append_dual_privacy_comparison,
    append_shadow_comparison,
    compare_dual_privacy_policy,
    compare_publication_shadow,
    evaluate_provenanced_publication_shadow,
)
from src.publish_components.models import PrivacyCheck
from src.publish_dashboard import run_publish_dashboard
from src.published_monitoring import (
    EXPECTED_COLUMNS,
    PUBLISHED_PARQUET_PATH,
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
from src.schema_contract_components.models import ContractCheck
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


@dataclass(frozen=True)
class PipelineRunMetadata:
    run_id: str
    started_at_utc: str
    completed_at_utc: str
    python_version: str
    platform: str
    git_commit: str


PIPELINE_STEPS = [
    PipelineStep("inventory", "Valida os CSVs de origem e gera o inventário bruto."),
    PipelineStep(
        "profiling", "Promove a camada standardized e gera o profiling exploratório."
    ),
    PipelineStep(
        "build", "Constrói a tabela analítica principal fact_orders_enriched."
    ),
    PipelineStep(
        "classify", "Materializa o inventário de classificação de dados do projeto."
    ),
    PipelineStep(
        "contracts", "Valida os contratos simples de schema das camadas principais."
    ),
    PipelineStep(
        "business_rules", "Executa regras de negócio declaradas por contrato."
    ),
    PipelineStep("quality", "Executa os checks de qualidade e salva os relatórios."),
    PipelineStep("publish", "Publica a camada minimizada para consumo do dashboard."),
    PipelineStep(
        "semantic",
        "Materializa marts semânticos publicados para logística, seller e cohort.",
    ),
    PipelineStep("monitor", "Monitora freshness e qualidade da camada publicada."),
    PipelineStep("scorecards", "Publica scorecards de governança por dataset."),
    PipelineStep("lineage", "Gera lineage técnico automatizado do pipeline."),
    PipelineStep("catalog", "Materializa a coleção local e o inventário catalogável."),
    PipelineStep(
        "queries", "Executa as queries SQL e exporta os resultados tabulares."
    ),
    PipelineStep("screenshots", "Converte os resultados das queries em imagens PNG."),
    PipelineStep("bi", "Exporta os datasets auxiliares para Power BI."),
]
PIPELINE_RESULTS_PATH = OPS_DIR / "operational_job_results.json"
PIPELINE_REPORT_PATH = DOCS_DIR / "reports" / "operational_job_report.md"
StepHandler = Callable[[], object]


_ACTIVE_GOVERNANCE_CONTEXT: ContextVar[PipelineGovernanceContext | None] = ContextVar(
    "pipeline_governance_context", default=None
)


@contextmanager
def activate_pipeline_governance_context(
    context: PipelineGovernanceContext,
) -> Iterator[PipelineGovernanceContext]:
    token = _ACTIVE_GOVERNANCE_CONTEXT.set(context)
    try:
        yield context
    finally:
        _ACTIVE_GOVERNANCE_CONTEXT.reset(token)


def _run_quality_step() -> None:
    fact_df = load_fact_table()
    results = run_quality_checks(fact_df)
    context = _ACTIVE_GOVERNANCE_CONTEXT.get()
    if context is not None:
        context.record_quality(results, produced_at=datetime.now(UTC))
    save_quality_results(results)
    save_quality_report(fact_df, results)


_ACTIVE_CONTENT_PROVENANCE_ENABLED: ContextVar[bool] = ContextVar(
    "content_provenance", default=False
)
_ACTIVE_SHADOW_ENABLED: ContextVar[bool] = ContextVar("shadow_telemetry", default=False)
_ACTIVE_DUAL_ENABLED: ContextVar[bool] = ContextVar("dual_telemetry", default=False)


def _capture_publish_material(
    context: PipelineGovernanceContext,
    source: pd.DataFrame,
    published: pd.DataFrame,
    results: list[PrivacyCheck],
    *,
    record_content_provenance: bool = False,
    content_provenance_path: Path = DEFAULT_DATASET_CONTENT_PROVENANCE_PATH,
) -> None:
    context.record_current_privacy(
        source, published, results, produced_at=datetime.now(UTC)
    )
    if record_content_provenance:
        try:
            material = build_dataset_content_provenance(
                run_id=context.run_id, source=source, published=published
            )
            append_dataset_content_provenance(
                material,
                timestamp_utc=context.started_at or datetime.now(UTC),
                output_path=content_provenance_path,
            )
        except Exception:
            LOGGER.warning(
                "Falha ao registrar dataset content provenance", exc_info=True
            )


def _run_monitor_step(
    context: PipelineGovernanceContext | None = None,
    *,
    record_shadow_telemetry: bool = False,
    shadow_telemetry_path: Path = DEFAULT_SHADOW_TELEMETRY_PATH,
    record_dual_privacy_telemetry: bool = False,
    dual_privacy_telemetry_path: Path = DEFAULT_DUAL_PRIVACY_TELEMETRY_PATH,
) -> None:
    results = run_monitoring()
    save_published_monitoring_results(results)
    save_published_monitoring_report(results)
    published_df = load_published_monitoring_frame()
    history_df = load_governance_history()
    freshness_result = next(
        (
            item
            for item in results
            if item.check_name == "published_file_freshness_hours"
        ),
        None,
    )
    freshness_status = (
        "fresh" if freshness_result and freshness_result.status == "PASS" else "stale"
    )
    observability_checks = evaluate_governance_observability(
        expected_columns=EXPECTED_COLUMNS,
        observed_columns=list(published_df.columns),
        freshness_status=freshness_status,
        history_df=history_df,
    )
    save_observability_results(observability_checks)
    failed_checks_count = int(sum(result.status == "FAIL" for result in results))
    latest_quality_score = (
        int(history_df["data_quality_score"].iloc[-1])
        if "data_quality_score" in history_df.columns and not history_df.empty
        else max(0, 100 - (failed_checks_count * 10))
    )
    latest_privacy_risk = (
        int(history_df["privacy_risk_score"].iloc[-1])
        if "privacy_risk_score" in history_df.columns and not history_df.empty
        else 0
    )
    context = context or _ACTIVE_GOVERNANCE_CONTEXT.get()
    if context is not None:
        context.record_monitoring(
            [MonitoringCheckResult(**asdict(result)) for result in results],
            produced_at=datetime.now(UTC),
        )
        context.record_observability(
            [ObservabilityCheck(**asdict(result)) for result in observability_checks],
            produced_at=datetime.now(UTC),
        )
    publication_status: CurrentMonitorDecision = (
        "Approved" if failed_checks_count == 0 else "Needs Review"
    )
    save_publication_decision_artifact(
        dataset_name="fact_orders_dashboard",
        publication_status=publication_status,
        data_quality_score=latest_quality_score,
        privacy_risk_score=latest_privacy_risk,
        failed_checks_count=failed_checks_count,
        timestamp_utc=datetime.now(UTC).isoformat(),
    )

    if context is not None:
        envelope = context.build_provenanced_evidence()
        timestamp = context.started_at or datetime.now(UTC)
        if record_shadow_telemetry or _ACTIVE_SHADOW_ENABLED.get():
            try:
                evaluation = evaluate_provenanced_publication_shadow(
                    envelope,
                    required_sources=SHADOW_REQUIRED_SOURCES,
                    current_monitor_decision=publication_status,
                )
                comparison = compare_publication_shadow(
                    evaluation,
                    validate_evidence_provenance(envelope, SHADOW_REQUIRED_SOURCES),
                )
                append_shadow_comparison(
                    comparison,
                    timestamp_utc=timestamp,
                    output_path=shadow_telemetry_path,
                )
            except Exception:
                LOGGER.warning("Falha ao registrar telemetria shadow", exc_info=True)
        if record_dual_privacy_telemetry or _ACTIVE_DUAL_ENABLED.get():
            try:
                dual = compare_dual_privacy_policy(
                    envelope.evidence,
                    inherent_privacy_risk_score=context.inherent_privacy_risk_score,
                    residual_privacy_risk_score=context.residual_privacy_risk_score,
                    inherent_provenance=context.inherent_privacy_risk_provenance,
                    residual_provenance=context.residual_privacy_risk_provenance,
                    current_run_id=context.run_id,
                )
                append_dual_privacy_comparison(
                    dual,
                    timestamp_utc=timestamp,
                    output_path=dual_privacy_telemetry_path,
                )
            except Exception:
                LOGGER.warning(
                    "Falha ao registrar telemetria dual privacy", exc_info=True
                )


def load_published_monitoring_frame() -> pd.DataFrame:
    if not PUBLISHED_PARQUET_PATH.exists():
        return pd.DataFrame()
    return pd.read_parquet(PUBLISHED_PARQUET_PATH)


def _run_queries_step() -> None:
    results = run_queries()
    save_execution_manifest(results)


STEP_HANDLERS: dict[str, StepHandler] = {
    "inventory": run_inventory,
    "profiling": run_profiling,
    "build": run_build,
    "publish": run_publish_dashboard,
    "semantic": run_semantic_layer,
    "classify": classification_main,
    "contracts": schema_contracts_main,
    "business_rules": business_rules_main,
    "quality": _run_quality_step,
    "monitor": _run_monitor_step,
    "scorecards": governance_scorecards_main,
    "lineage": lineage_main,
    "catalog": catalog_main,
    "queries": _run_queries_step,
    "screenshots": export_all_query_result_images,
    "bi": run_export,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Runner principal do pipeline analítico Olist."
    )
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
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continua a execução mesmo quando uma etapa falha e consolida as falhas no relatório final.",
    )
    for flag in (
        "--record-shadow-telemetry",
        "--record-dual-privacy-telemetry",
        "--record-content-provenance",
    ):
        parser.add_argument(
            flag,
            action="store_true",
            help="Persiste diagnostico da execucao atual, sem alterar a autoridade de publicacao.",
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
    handler = STEP_HANDLERS.get(step_name)
    if handler is None:  # pragma: no cover
        raise ValueError(f"Etapa desconhecida: {step_name}")
    if step_name == "publish" and _ACTIVE_GOVERNANCE_CONTEXT.get() is not None:
        context = _ACTIVE_GOVERNANCE_CONTEXT.get()
        assert context is not None
        publish_context = context
        run_publish_dashboard(
            capture_privacy_material_fn=lambda source, published, checks: (
                _capture_publish_material(
                    publish_context,
                    source,
                    published,
                    checks,
                    record_content_provenance=_ACTIVE_CONTENT_PROVENANCE_ENABLED.get(),
                )
            )
        )
    elif step_name == "contracts" and _ACTIVE_GOVERNANCE_CONTEXT.get() is not None:
        context = _ACTIVE_GOVERNANCE_CONTEXT.get()
        assert context is not None
        schema_contracts_main(
            capture_results_fn=lambda results: context.record_schema(
                [ContractCheck(**asdict(result)) for result in results],
                produced_at=datetime.now(UTC),
            )
        )
    else:
        handler()


def resolve_git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            check=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip() or "unknown"


def build_pipeline_run_id(started_at: datetime) -> str:
    return started_at.strftime("run-%Y%m%dT%H%M%SZ")


def build_run_metadata(
    started_at: datetime, completed_at: datetime
) -> PipelineRunMetadata:
    return PipelineRunMetadata(
        run_id=build_pipeline_run_id(started_at),
        started_at_utc=started_at.isoformat(),
        completed_at_utc=completed_at.isoformat(),
        python_version=platform.python_version(),
        platform=platform.platform(),
        git_commit=resolve_git_commit(),
    )


def save_pipeline_execution_report(
    selected_steps: list[str],
    executions: list[StepExecution],
    metadata: PipelineRunMetadata,
) -> tuple[Path, Path]:
    ensure_directory(OPS_DIR)
    ensure_directory(PIPELINE_REPORT_PATH.parent)
    PIPELINE_RESULTS_PATH.write_text(
        json.dumps(
            {
                "metadata": asdict(metadata),
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
        f"- Run ID: `{metadata.run_id}`",
        f"- Inicio UTC: `{metadata.started_at_utc}`",
        f"- Fim UTC: `{metadata.completed_at_utc}`",
        f"- Python: `{metadata.python_version}`",
        f"- Plataforma: `{metadata.platform}`",
        f"- Git commit: `{metadata.git_commit}`",
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


def run_selected_steps(
    selected_steps: list[str], continue_on_error: bool = False
) -> list[StepExecution]:
    executions: list[StepExecution] = []
    failures: list[StepExecution] = []
    for step_name in selected_steps:
        started_at = perf_counter()
        LOGGER.info("Iniciando etapa: %s", step_name)
        try:
            execute_step(step_name)
        except Exception as exc:
            elapsed = perf_counter() - started_at
            failure = StepExecution(
                name=step_name,
                status="FAIL",
                duration_seconds=elapsed,
                error_message=str(exc),
            )
            executions.append(failure)
            failures.append(failure)
            LOGGER.exception("Etapa falhou: %s | duração=%.2fs", step_name, elapsed)
            if not continue_on_error:
                raise
            continue
        elapsed = perf_counter() - started_at
        executions.append(
            StepExecution(name=step_name, status="PASS", duration_seconds=elapsed)
        )
        LOGGER.info("Etapa concluída: %s | duração=%.2fs", step_name, elapsed)
    if failures and continue_on_error:
        failed_names = ", ".join(execution.name for execution in failures)
        raise RuntimeError(f"Pipeline finalizado com falhas nas etapas: {failed_names}")
    return executions


def main() -> None:
    args = parse_args()
    if args.list_steps:
        list_steps()
        return

    configure_logging()
    PATHS.validate()
    selected_steps = resolve_steps(args.steps)
    LOGGER.info("Pipeline selecionado: %s", ", ".join(selected_steps))
    started_at = datetime.now(UTC)
    context = PipelineGovernanceContext(
        run_id=build_pipeline_run_id(started_at),
        started_at=started_at,
    )
    diagnostic_tokens = [
        (variable, variable.set(bool(getattr(args, name, False))))
        for variable, name in (
            (_ACTIVE_CONTENT_PROVENANCE_ENABLED, "record_content_provenance"),
            (_ACTIVE_SHADOW_ENABLED, "record_shadow_telemetry"),
            (_ACTIVE_DUAL_ENABLED, "record_dual_privacy_telemetry"),
        )
    ]
    with activate_pipeline_governance_context(context):
        executions: list[StepExecution] = []
        try:
            executions = run_selected_steps(
                selected_steps, continue_on_error=args.continue_on_error
            )
        finally:
            for variable, token in reversed(diagnostic_tokens):
                variable.reset(token)
            completed_at = datetime.now(UTC)
            metadata = build_run_metadata(started_at, completed_at)
            save_pipeline_execution_report(selected_steps, executions, metadata)


if __name__ == "__main__":
    main()
