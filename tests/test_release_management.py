from __future__ import annotations

import pytest

from src.release_management import resolve_promotion_plan


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
