from __future__ import annotations

import pytest

import src.release_management as release_management
from src.release_management import normalize_source_branch, resolve_promotion_plan


def test_resolve_promotion_plan_for_prod() -> None:
    plan = resolve_promotion_plan("prod", "refs/heads/main", "main")

    assert plan.deployment_branch == "streamlit-prod"
    assert plan.github_environment == "streamlit-production"


def test_resolve_promotion_plan_normalizes_master_to_main() -> None:
    plan = resolve_promotion_plan("prod", "refs/heads/master", "master")

    assert plan.source_branch == "main"


def test_resolve_promotion_plan_rejects_wrong_source_branch() -> None:
    with pytest.raises(ValueError, match="exige source branch"):
        resolve_promotion_plan("prod", "refs/heads/develop", "develop")


def test_resolve_promotion_plan_rejects_invalid_environment() -> None:
    with pytest.raises(ValueError, match="Ambiente de deploy inválido"):
        resolve_promotion_plan("staging", "refs/heads/main", "main")


def test_normalize_source_branch_strips_refs_heads_prefix() -> None:
    assert normalize_source_branch("refs/heads/develop") == "develop"


def test_normalize_source_branch_passthrough_for_plain_name() -> None:
    assert normalize_source_branch("release") == "release"


def test_resolve_promotion_plan_for_dev_and_stage() -> None:
    dev_plan = resolve_promotion_plan("dev", "refs/heads/develop", "develop")
    stage_plan = resolve_promotion_plan("stage", "refs/heads/release", "release")

    assert dev_plan.deployment_branch == "streamlit-dev"
    assert stage_plan.deployment_branch == "streamlit-stage"


def test_main_writes_github_output_file(tmp_path, monkeypatch) -> None:
    output_file = tmp_path / "github_output.txt"
    monkeypatch.setattr(
        "sys.argv",
        [
            "release_management.py",
            "--target-environment", "prod",
            "--source-ref", "refs/heads/main",
            "--source-branch", "main",
            "--github-output", str(output_file),
        ],
    )

    release_management.main()

    content = output_file.read_text(encoding="utf-8")
    assert "deployment_branch=streamlit-prod" in content
    assert "github_environment=streamlit-production" in content
    assert "target_environment=prod" in content
