from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.config import ROOT_DIR

POLICIES_ROOT = ROOT_DIR / "contracts" / "governance" / "policies"
VERSION_PATTERN = re.compile(r"^v(?P<version>\d+)\.json$")


def _extract_version(path: Path) -> int | None:
    match = VERSION_PATTERN.match(path.name)
    if not match:
        return None
    return int(match.group("version"))


def list_policy_versions(domain: str, policies_root: Path = POLICIES_ROOT) -> list[Path]:
    domain_dir = policies_root / domain
    if not domain_dir.exists():
        raise FileNotFoundError(f"Domínio de política LGPD inexistente: {domain_dir}")
    versioned = [path for path in domain_dir.glob("v*.json") if _extract_version(path) is not None]
    if not versioned:
        raise FileNotFoundError(f"Nenhuma política LGPD versionada encontrada em: {domain_dir}")
    return sorted(versioned, key=lambda path: _extract_version(path) or 0)


def load_policy(domain: str, version: int | None = None, policies_root: Path = POLICIES_ROOT) -> dict[str, Any]:
    versions = list_policy_versions(domain, policies_root=policies_root)
    if version is None:
        selected = versions[-1]
    else:
        selected = policies_root / domain / f"v{version}.json"
        if selected not in versions:
            raise FileNotFoundError(f"Versão da política LGPD não encontrada: {selected}")
    policy = json.loads(selected.read_text(encoding="utf-8"))
    policy["_policy_path"] = str(selected)
    policy["_policy_version"] = _extract_version(selected)
    return policy


def validate_policy_shape(policy: dict[str, Any]) -> None:
    required_fields = {
        "policy_id",
        "domain",
        "version",
        "effective_date",
        "dataset_name",
        "required_columns",
        "forbidden_columns",
        "pseudonymized_columns",
        "default_fill_values",
        "rules",
        "owner",
    }
    missing = sorted(field for field in required_fields if field not in policy)
    if missing:
        raise ValueError(f"Política LGPD inválida. Campos ausentes: {missing}")

