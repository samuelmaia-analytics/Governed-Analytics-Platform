from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.observability_components.models import ObservabilityCheck
from src.observability_components.outputs import save_observability_results


def _checks() -> list[ObservabilityCheck]:
    return [
        ObservabilityCheck("ok", "PASS", "low", "ação", "esperado", "válido"),
        ObservabilityCheck("bad", "FAIL", "high", 2.0, 1.0, "falhou"),
    ]


def test_save_results_writes_current_json_schema_and_utf8(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "observability.json"
    ensured: list[Path] = []

    def ensure(path: Path) -> Path:
        ensured.append(path)
        path.mkdir(parents=True)
        return path

    returned = save_observability_results(
        _checks(), output_path=output_path, ensure_directory_fn=ensure
    )
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert returned == output_path
    assert ensured == [output_path.parent]
    assert list(payload) == ["generated_at_utc", "total_checks", "failed_checks", "checks"]
    assert payload["total_checks"] == 2
    assert payload["failed_checks"] == 1
    assert payload["checks"][0]["metric_value"] == "ação"
    assert "\\u00e7" not in output_path.read_text(encoding="utf-8")


def test_save_results_propagates_directory_error(tmp_path: Path) -> None:
    def fail(_path: Path) -> Path:
        raise OSError("cannot create output directory")

    with pytest.raises(OSError, match="cannot create output directory"):
        save_observability_results(
            _checks(), output_path=tmp_path / "result.json", ensure_directory_fn=fail
        )


def test_save_results_propagates_write_error(tmp_path: Path) -> None:
    output_path = tmp_path / "directory"
    output_path.mkdir()

    with pytest.raises((IsADirectoryError, PermissionError)):
        save_observability_results(
            _checks(), output_path=output_path, ensure_directory_fn=lambda path: path
        )
