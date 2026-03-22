from __future__ import annotations

from src.run_case_pipeline import PIPELINE_STEPS, resolve_steps


def test_resolve_steps_returns_full_pipeline_when_none_provided() -> None:
    steps = resolve_steps(None)

    assert steps == [step.name for step in PIPELINE_STEPS]
    assert "publish" in steps


def test_resolve_steps_preserves_explicit_selection_order() -> None:
    steps = resolve_steps(["build", "quality"])

    assert steps == ["build", "quality"]
