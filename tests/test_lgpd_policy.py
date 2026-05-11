from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.lgpd_policy import list_policy_versions, load_policy, validate_policy_shape


def test_load_policy_defaults_to_latest_version(tmp_path: Path) -> None:
    policy_dir = tmp_path / "policies" / "retail"
    policy_dir.mkdir(parents=True)
    base_payload = {
        "policy_id": "id",
        "domain": "retail",
        "effective_date": "2026-01-01",
        "dataset_name": "dataset",
        "required_columns": [],
        "forbidden_columns": [],
        "pseudonymized_columns": {},
        "default_fill_values": {},
        "rules": [],
        "owner": "owner@example.com",
    }
    (policy_dir / "v1.json").write_text(
        json.dumps({**base_payload, "version": 1}), encoding="utf-8"
    )
    (policy_dir / "v2.json").write_text(
        json.dumps({**base_payload, "version": 2}), encoding="utf-8"
    )

    loaded = load_policy(domain="retail", policies_root=tmp_path / "policies")

    assert loaded["version"] == 2
    assert loaded["_policy_version"] == 2


def test_validate_policy_shape_raises_for_missing_fields() -> None:
    with pytest.raises(ValueError, match="Campos ausentes"):
        validate_policy_shape({"domain": "retail"})


def test_list_policy_versions_raises_when_domain_absent(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Domínio de política LGPD inexistente"):
        list_policy_versions("missing", policies_root=tmp_path / "policies")
