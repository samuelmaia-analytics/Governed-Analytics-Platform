from __future__ import annotations

from pathlib import Path


def test_requirements_include_cli_validation_tooling() -> None:
    requirements_path = Path(__file__).resolve().parent.parent / "requirements.txt"

    requirements = {
        line.strip()
        for line in requirements_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "ruff>=0.12,<0.13" in requirements


def test_requirements_lock_exists_with_pinned_core_dependencies() -> None:
    requirements_lock_path = Path(__file__).resolve().parent.parent / "requirements.lock"

    requirements_lock = {
        line.strip()
        for line in requirements_lock_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert "pandas==2.3.3" in requirements_lock
    assert "requests==2.32.5" in requirements_lock
