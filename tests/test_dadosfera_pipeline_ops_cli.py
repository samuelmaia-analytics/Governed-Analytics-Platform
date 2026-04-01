from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_dadosfera_pipeline_ops_help_runs_as_direct_script() -> None:
    project_root = Path(__file__).resolve().parent.parent

    completed = subprocess.run(
        [sys.executable, "src/dadosfera_pipeline_ops.py", "--help"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Opera pipelines nativos da Dadosfera via API" in completed.stdout
