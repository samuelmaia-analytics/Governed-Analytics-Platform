from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from pathlib import Path
import sys
from time import perf_counter

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.catalog import main as catalog_main
from src.data_classification import main as classification_main
from src.export_power_bi import run_export
from src.export_query_result_images import export_all_query_result_images
from src.ingest import configure_logging, run_inventory
from src.publish_dashboard import run_publish_dashboard
from src.preprocess import run_profiling
from src.build_analytics import run_build
from src.quality import load_fact_table, run_quality_checks, save_quality_report, save_quality_results
from src.run_analytics_queries import run_queries, save_execution_manifest
from src.schema_contracts import main as schema_contracts_main


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PipelineStep:
    name: str
    description: str


PIPELINE_STEPS = [
    PipelineStep("inventory", "Valida os CSVs de origem e gera o inventário bruto."),
    PipelineStep("profiling", "Promove a camada standardized e gera o profiling exploratório."),
    PipelineStep("build", "Constrói a tabela analítica principal fact_orders_enriched."),
    PipelineStep("publish", "Publica a camada minimizada para consumo do dashboard."),
    PipelineStep("classify", "Materializa o inventário de classificação de dados do projeto."),
    PipelineStep("contracts", "Valida os contratos simples de schema das camadas principais."),
    PipelineStep("quality", "Executa os checks de qualidade e salva os relatórios."),
    PipelineStep("catalog", "Materializa a coleção local e o inventário catalogável."),
    PipelineStep("queries", "Executa as queries SQL e exporta os resultados tabulares."),
    PipelineStep("screenshots", "Converte os resultados das queries em imagens PNG."),
    PipelineStep("bi", "Exporta os datasets auxiliares para Power BI."),
]


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


def run_selected_steps(selected_steps: list[str]) -> None:
    for step_name in selected_steps:
        started_at = perf_counter()
        LOGGER.info("Iniciando etapa: %s", step_name)

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
        elif step_name == "classify":
            classification_main()
        elif step_name == "contracts":
            schema_contracts_main()
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

        elapsed = perf_counter() - started_at
        LOGGER.info("Etapa concluída: %s | duração=%.2fs", step_name, elapsed)


def main() -> None:
    args = parse_args()
    if args.list_steps:
        list_steps()
        return

    configure_logging()
    selected_steps = resolve_steps(args.steps)
    LOGGER.info("Pipeline selecionado: %s", ", ".join(selected_steps))
    run_selected_steps(selected_steps)


if __name__ == "__main__":
    main()
