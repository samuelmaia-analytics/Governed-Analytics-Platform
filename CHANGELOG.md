# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Interactive column analysis tab in EDA page (histogram, boxplot, bar chart per column)
- Search and LGPD classification filter in Data Catalog page
- Trend deltas on Executive Overview metrics (risk score, quality score, failures vs. previous snapshot)
- Data freshness indicator (sidebar + Executive Overview)
- Suppressed columns metric (LGPD-active protection count)
- Governance Report page now renders markdown properly with per-report expanders
- LGPD & Privacy Risk page restructured into tabs (Score & Risk / Classifications / Transformation Preview)
- Governance Control Center: historical trends moved to collapsible expander

### Fixed
- MyPy errors in `publish_dashboard.py`, `run_platform_pipeline.py`, `run_analytics_queries.py`, `schema_contracts.py`
- Ruff formatting applied across all source files
- `StepHandler` type corrected from `Callable[[], None]` to `Callable[[], object]`

## [0.1.0] - 2025-05-01

### Added
- Complete governance pipeline with LGPD-inspired classification
- Explainable privacy risk scoring with per-component breakdown
- Declarative YAML data quality checks
- Streamlit executive interface with 7 governance-focused pages
- CI with Pytest, Ruff, MyPy, and GitHub Actions
- Data contracts for standardized, curated, and published layers
- Publication gate with explicit Approved / Needs Review / Blocked states
- Governance history tracking and snapshot audit trail
- Dadosfera catalog sync integration
- Power BI export artifacts
- Bilingual documentation (English + Portuguese)
