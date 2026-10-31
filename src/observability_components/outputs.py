from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from src.observability_components.models import ObservabilityCheck


def save_observability_results(
    checks: list[ObservabilityCheck],
    *,
    output_path: Path,
    ensure_directory_fn: Callable[[Path], Path],
) -> Path:
    ensure_directory_fn(output_path.parent)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_checks": len(checks),
        "failed_checks": sum(1 for item in checks if item.status == "FAIL"),
        "checks": [asdict(item) for item in checks],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return output_path

