from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.report_generator import generate_markdown_reports


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_email": ["ana@example.com", "bruno@example.com"],
            "cpf": ["123.456.789-09", "987.654.321-00"],
            "revenue": [100.0, 200.0],
            "status": ["completed", "completed"],
        }
    )


def test_generate_markdown_reports_creates_expected_files(tmp_path: Path) -> None:
    paths = generate_markdown_reports(_sample_df(), docs_dir=tmp_path)

    assert set(paths.keys()) == {"data_dictionary", "lgpd_controls", "data_quality_report", "lgpd_ripd_sample"}
    for path in paths.values():
        assert path.exists()


def test_generated_lgpd_controls_contains_required_sections(tmp_path: Path) -> None:
    paths = generate_markdown_reports(_sample_df(), docs_dir=tmp_path)
    content = paths["lgpd_controls"].read_text(encoding="utf-8")

    assert "# LGPD Controls" in content
    assert "## LGPD Classification by Column" in content
    assert "## Governance Recommendations" in content


def test_generated_data_quality_report_contains_risks_and_next_steps(tmp_path: Path) -> None:
    paths = generate_markdown_reports(_sample_df(), docs_dir=tmp_path)
    content = paths["data_quality_report"].read_text(encoding="utf-8")

    assert "# Data Quality Report" in content
    assert "## Risks Found" in content
    assert "## Next Steps" in content


def test_generated_ripd_sample_contains_core_sections(tmp_path: Path) -> None:
    paths = generate_markdown_reports(_sample_df(), docs_dir=tmp_path)
    content = paths["lgpd_ripd_sample"].read_text(encoding="utf-8")
    assert "Mini RIPD" in content
    assert "Inventário de Tratamento" in content
    assert "Matriz de Risco" in content
