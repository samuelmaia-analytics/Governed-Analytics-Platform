from __future__ import annotations

from pathlib import Path

import pytest

from src.config import ProjectPaths


def test_project_paths_from_root_builds_expected_structure(tmp_path: Path) -> None:
    paths = ProjectPaths.from_root(tmp_path)

    assert paths.data_dir == tmp_path / "data"
    assert paths.ops_dir == tmp_path / "data" / "curated" / "ops"
    assert paths.genai_input_dir == tmp_path / "data" / "external" / "genai"


def test_project_paths_validate_requires_enterprise_baseline_structure(
    tmp_path: Path,
) -> None:
    paths = ProjectPaths.from_root(tmp_path)

    with pytest.raises(FileNotFoundError, match="Estrutura base do projeto ausente"):
        paths.validate()


def test_project_paths_validate_accepts_existing_baseline_structure(
    tmp_path: Path,
) -> None:
    for directory in ("data", "sql", "docs"):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)

    ProjectPaths.from_root(tmp_path).validate()
