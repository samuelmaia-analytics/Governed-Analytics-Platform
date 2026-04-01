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
