from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from src.config import DOCS_DIR, ROOT_DIR
from src.dadosfera_catalog_sync import (
    DEFAULT_MANIFEST_PATH,
    CatalogAssetSpec,
    DadosferaMaestroClient,
    SyncResult,
    load_manifest,
    sync_assets,
)
from src.dadosfera_pipeline_ops import (
    DadosferaPipelineClient,
    find_pipeline_by_name,
    load_json_file,
    resolve_pipeline_id,
)
from src.observability import configure_logging
from src.settings import load_app_settings

DEFAULT_PIPELINE_DEFINITION_PATH = (
    ROOT_DIR
    / "contracts"
    / "dadosfera"
    / "pipelines"
    / "fact_orders_dashboard_s3_parquet_pipeline.json"
)
DEFAULT_REPORT_PATH = DOCS_DIR / "reports" / "platform_publication.md"


@dataclass(frozen=True)
class PlatformPublicationResult:
    stage: str
    status: str
    details: str


def to_project_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT_DIR).as_posix()
    except ValueError:
        return path.as_posix()


def build_catalog_client(base_url: str) -> DadosferaMaestroClient:
    settings = load_app_settings().dadosfera
    settings.validate_credentials(operation="platform_publication_catalog")
    return DadosferaMaestroClient(
        base_url=base_url,
        username=settings.username,
        password=settings.password,
        totp=settings.totp,
        access_token=settings.effective_access_token,
    )


def build_pipeline_client(base_url: str) -> DadosferaPipelineClient:
    settings = load_app_settings().dadosfera
    settings.validate_credentials(operation="platform_publication_pipeline")
    return DadosferaPipelineClient(
        base_url=base_url,
        username=settings.username,
        password=settings.password,
        totp=settings.totp,
        access_token=settings.effective_access_token,
    )


def run_catalog_publication(
    *,
    base_url: str,
    manifest_path: Path,
    dry_run: bool,
) -> tuple[list[SyncResult], PlatformPublicationResult]:
    assets: list[CatalogAssetSpec] = load_manifest(manifest_path)
    client = build_catalog_client(base_url)
    client.sign_in()
    results = sync_assets(client=client, assets=assets, dry_run=dry_run)
    action_summary = ", ".join(result.action for result in results) or "no_changes"
    return results, PlatformPublicationResult(
        stage="catalog_sync",
        status="DRY_RUN" if dry_run else "SUCCESS",
        details=f"{len(results)} ativos processados ({action_summary})",
    )


def run_pipeline_publication(
    *,
    base_url: str,
    definition_path: Path,
    dry_run: bool,
    execute_pipeline: bool,
) -> PlatformPublicationResult:
    definition = load_json_file(definition_path)
    pipeline_name = str(definition.get("name") or "").strip()
    if not pipeline_name:
        raise RuntimeError("A definição de pipeline precisa conter o campo `name`.")

    client = build_pipeline_client(base_url)
    client.sign_in()
    existing = find_pipeline_by_name(client, pipeline_name)

    if dry_run:
        status = "DRY_RUN"
        details = (
            f"pipeline `{pipeline_name}` {'já existe' if existing else 'seria criada'}"
        )
        if execute_pipeline:
            details += " e seria executada"
        return PlatformPublicationResult(
            stage="pipeline_publication", status=status, details=details
        )

    response = existing or client.create_pipeline(definition)
    pipeline_id = resolve_pipeline_id(response)
    details = f"pipeline `{pipeline_name}` pronta com id `{pipeline_id}`"
    if execute_pipeline:
        run_response = client.run_pipeline(pipeline_id, {})
        run_id = (
            run_response.get("id")
            or run_response.get("run_id")
            or run_response.get("uuid")
            or "unknown"
        )
        details += f" | execução disparada `{run_id}`"
    return PlatformPublicationResult(
        stage="pipeline_publication", status="SUCCESS", details=details
    )


def render_report(
    *,
    target_environment: str,
    manifest_path: Path,
    definition_path: Path,
    results: list[PlatformPublicationResult],
) -> str:
    lines = [
        "# Publicação em Ambiente de Plataforma",
        "",
        f"- Ambiente alvo: `{target_environment}`",
        f"- Manifesto de catálogo: `{to_project_path(manifest_path)}`",
        f"- Definição de pipeline: `{to_project_path(definition_path)}`",
        "",
        "| Etapa | Status | Detalhes |",
        "| --- | --- | --- |",
    ]
    for result in results:
        lines.append(f"| `{result.stage}` | `{result.status}` | {result.details} |")
    return "\n".join(lines) + "\n"


def save_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    settings = load_app_settings()
    parser = argparse.ArgumentParser(
        description="Orquestra sync de catálogo e deploy idempotente de pipeline para publicação em ambiente de plataforma."
    )
    parser.add_argument("--base-url", default=settings.dadosfera.base_url)
    parser.add_argument("--target-environment", default="prod")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument(
        "--pipeline-definition", type=Path, default=DEFAULT_PIPELINE_DEFINITION_PATH
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-catalog-sync", action="store_true")
    parser.add_argument("--skip-pipeline-publication", action="store_true")
    parser.add_argument("--execute-pipeline", action="store_true")
    return parser.parse_args()


def main() -> None:
    configure_logging()
    args = parse_args()

    results: list[PlatformPublicationResult] = []
    if not args.skip_catalog_sync:
        _, catalog_result = run_catalog_publication(
            base_url=args.base_url,
            manifest_path=args.manifest.resolve(),
            dry_run=args.dry_run,
        )
        results.append(catalog_result)

    if not args.skip_pipeline_publication:
        pipeline_result = run_pipeline_publication(
            base_url=args.base_url,
            definition_path=args.pipeline_definition.resolve(),
            dry_run=args.dry_run,
            execute_pipeline=args.execute_pipeline,
        )
        results.append(pipeline_result)

    report = render_report(
        target_environment=args.target_environment,
        manifest_path=args.manifest.resolve(),
        definition_path=args.pipeline_definition.resolve(),
        results=results,
    )
    save_report(args.report.resolve(), report)
    print(report)


if __name__ == "__main__":
    main()
