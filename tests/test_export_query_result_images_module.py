from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.export_query_result_images as export_images


def test_validate_input_files_requires_existing_csvs(tmp_path: Path, monkeypatch) -> None:
    query_dir = tmp_path / "query_results"
    monkeypatch.setattr(export_images, "QUERY_RESULTS_DIR", query_dir)

    with pytest.raises(FileNotFoundError):
        export_images.validate_input_files()

    query_dir.mkdir()
    (query_dir / "query_execution_manifest.csv").write_text("x\n1\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        export_images.validate_input_files()

    (query_dir / "01_demo.csv").write_text("a,b\n1,2\n", encoding="utf-8")
    assert [path.name for path in export_images.validate_input_files()] == ["01_demo.csv"]


def test_formatting_preview_and_figure_size_helpers() -> None:
    df = pd.DataFrame({"col": ["texto longo " * 4], "value": [10.1234]})

    assert export_images.format_value(10.1234) == "10.12"
    assert export_images.format_value(pd.NA) == ""
    assert "\n" in export_images.wrap_cell_text("texto longo " * 6)
    preview = export_images.prepare_display_df(df)
    width, height = export_images.compute_figure_size(preview)

    assert len(preview) == 1
    assert width >= 12
    assert height >= 2.8


def test_render_and_export_csv_as_png(tmp_path: Path, monkeypatch) -> None:
    csv_path = tmp_path / "01_demo.csv"
    output_dir = tmp_path / "images"
    pd.DataFrame({"a": [1, 2], "b": ["x", "y"]}).to_csv(csv_path, index=False)
    monkeypatch.setattr(export_images, "OUTPUT_DIR", output_dir)

    exported = export_images.export_csv_as_png(csv_path)

    assert exported.output_png.exists()
    assert exported.rows_rendered == 2
    assert exported.total_columns == 2


def test_export_all_query_result_images_and_main(tmp_path: Path, monkeypatch) -> None:
    query_dir = tmp_path / "query_results"
    query_dir.mkdir()
    pd.DataFrame({"a": [1]}).to_csv(query_dir / "01_demo.csv", index=False)
    monkeypatch.setattr(export_images, "QUERY_RESULTS_DIR", query_dir)
    monkeypatch.setattr(export_images, "OUTPUT_DIR", tmp_path / "images")

    results = export_images.export_all_query_result_images()

    assert len(results) == 1
    export_images.main()
    assert (tmp_path / "images" / "01_demo.png").exists()
