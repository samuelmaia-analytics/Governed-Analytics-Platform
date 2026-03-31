from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root_dir: Path
    data_dir: Path
    raw_data_dir: Path
    landing_dir: Path
    standardized_dir: Path
    staging_dir: Path
    curated_dir: Path
    published_dir: Path
    analytics_dir: Path
    quality_dir: Path
    query_results_dir: Path
    catalog_dir: Path
    ops_dir: Path
    published_dashboard_dir: Path
    published_monitoring_dir: Path
    published_semantic_dir: Path
    profiling_dir: Path
    external_data_dir: Path
    screenshots_dir: Path
    sql_dir: Path
    docs_dir: Path
    genai_input_dir: Path
    genai_output_dir: Path

    @classmethod
    def from_root(cls, root_dir: Path) -> "ProjectPaths":
        data_dir = root_dir / "data"
        raw_data_dir = data_dir / "raw"
        landing_dir = raw_data_dir / "landing"
        staging_dir = data_dir / "staging"
        curated_dir = data_dir / "curated"
        published_dir = data_dir / "published"
        external_data_dir = data_dir / "external"
        return cls(
            root_dir=root_dir,
            data_dir=data_dir,
            raw_data_dir=raw_data_dir,
            landing_dir=landing_dir,
            standardized_dir=data_dir / "standardized",
            staging_dir=staging_dir,
            curated_dir=curated_dir,
            published_dir=published_dir,
            analytics_dir=curated_dir / "analytics",
            quality_dir=curated_dir / "quality",
            query_results_dir=curated_dir / "query_results",
            catalog_dir=curated_dir / "catalog",
            ops_dir=curated_dir / "ops",
            published_dashboard_dir=published_dir / "dashboard",
            published_monitoring_dir=published_dir / "monitoring",
            published_semantic_dir=published_dir / "semantic",
            profiling_dir=staging_dir / "profiling",
            external_data_dir=external_data_dir,
            screenshots_dir=data_dir / "screenshots",
            sql_dir=root_dir / "sql",
            docs_dir=root_dir / "docs",
            genai_input_dir=external_data_dir / "genai",
            genai_output_dir=curated_dir / "genai",
        )

    def validate(self) -> None:
        required_dirs = {
            "root_dir": self.root_dir,
            "data_dir": self.data_dir,
            "sql_dir": self.sql_dir,
            "docs_dir": self.docs_dir,
        }
        missing = [name for name, path in required_dirs.items() if not path.exists()]
        if missing:
            missing_paths = ", ".join(f"{name}={required_dirs[name]}" for name in missing)
            raise FileNotFoundError(f"Estrutura base do projeto ausente: {missing_paths}")


def load_project_paths() -> ProjectPaths:
    configured_root = os.getenv("PROJECT_ROOT_DIR")
    root_dir = Path(configured_root).resolve() if configured_root else Path(__file__).resolve().parent.parent
    return ProjectPaths.from_root(root_dir)


PATHS = load_project_paths()
ROOT_DIR = PATHS.root_dir
DATA_DIR = PATHS.data_dir
RAW_DATA_DIR = PATHS.raw_data_dir
LANDING_DIR = PATHS.landing_dir
STANDARDIZED_DIR = PATHS.standardized_dir
STAGING_DIR = PATHS.staging_dir
CURATED_DIR = PATHS.curated_dir
PUBLISHED_DIR = PATHS.published_dir
ANALYTICS_DIR = PATHS.analytics_dir
QUALITY_DIR = PATHS.quality_dir
QUERY_RESULTS_DIR = PATHS.query_results_dir
CATALOG_DIR = PATHS.catalog_dir
OPS_DIR = PATHS.ops_dir
PUBLISHED_DASHBOARD_DIR = PATHS.published_dashboard_dir
PUBLISHED_MONITORING_DIR = PATHS.published_monitoring_dir
PUBLISHED_SEMANTIC_DIR = PATHS.published_semantic_dir
PROFILING_DIR = PATHS.profiling_dir
EXTERNAL_DATA_DIR = PATHS.external_data_dir
SCREENSHOTS_DIR = PATHS.screenshots_dir
SQL_DIR = PATHS.sql_dir
DOCS_DIR = PATHS.docs_dir
GENAI_INPUT_DIR = PATHS.genai_input_dir
GENAI_OUTPUT_DIR = PATHS.genai_output_dir
