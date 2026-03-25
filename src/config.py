from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
LANDING_DIR = RAW_DATA_DIR / "landing"
STANDARDIZED_DIR = DATA_DIR / "standardized"
STAGING_DIR = DATA_DIR / "staging"
CURATED_DIR = DATA_DIR / "curated"
PUBLISHED_DIR = DATA_DIR / "published"
ANALYTICS_DIR = CURATED_DIR / "analytics"
QUALITY_DIR = CURATED_DIR / "quality"
QUERY_RESULTS_DIR = CURATED_DIR / "query_results"
CATALOG_DIR = CURATED_DIR / "catalog"
PUBLISHED_DASHBOARD_DIR = PUBLISHED_DIR / "dashboard"
PROFILING_DIR = STAGING_DIR / "profiling"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
SQL_DIR = ROOT_DIR / "sql"
DOCS_DIR = ROOT_DIR / "docs"
GENAI_INPUT_DIR = EXTERNAL_DATA_DIR / "genai"
GENAI_OUTPUT_DIR = CURATED_DIR / "genai"
