from __future__ import annotations

from pathlib import Path


def test_pyproject_declares_dev_tooling() -> None:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")

    assert "dev = [" in content
    assert '"ruff>=0.12,<0.16"' in content


def test_uv_lock_exists_with_pinned_core_dependencies() -> None:
    uv_lock_path = Path(__file__).resolve().parent.parent / "uv.lock"

    uv_lock = {
        line.strip()
        for line in uv_lock_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert any('name = "pandas"' in line for line in uv_lock)
    assert any('name = "requests"' in line for line in uv_lock)
