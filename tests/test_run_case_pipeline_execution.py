from __future__ import annotations

import pytest

import src.run_case_pipeline as pipeline


def test_run_selected_steps_executes_requested_functions_in_order(monkeypatch) -> None:
    called_steps: list[str] = []

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "inventory", lambda: called_steps.append("inventory"))
    monkeypatch.setitem(pipeline.STEP_HANDLERS, "build", lambda: called_steps.append("build"))
    monkeypatch.setitem(pipeline.STEP_HANDLERS, "publish", lambda: called_steps.append("publish"))

    pipeline.run_selected_steps(["inventory", "build", "publish"])

    assert called_steps == ["inventory", "build", "publish"]


def test_run_selected_steps_executes_semantic_and_monitor_steps(monkeypatch) -> None:
    called_steps: list[str] = []

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "semantic", lambda: called_steps.append("semantic"))

    def monitor_handler() -> None:
        called_steps.append("monitor")
        called_steps.append("save_results")
        called_steps.append("save_report")

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "monitor", monitor_handler)

    pipeline.run_selected_steps(["semantic", "monitor"])

    assert called_steps == ["semantic", "monitor", "save_results", "save_report"]


def test_run_selected_steps_executes_quality_flow(monkeypatch) -> None:
    called_steps: list[str] = []

    def quality_handler() -> None:
        called_steps.append("quality_checks:fact_df")
        called_steps.append("save_results:quality_result")
        called_steps.append("save_report:fact_df:quality_result")

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "quality", quality_handler)

    pipeline.run_selected_steps(["quality"])

    assert called_steps == [
        "quality_checks:fact_df",
        "save_results:quality_result",
        "save_report:fact_df:quality_result",
    ]


def test_run_selected_steps_raises_immediately_without_continue_on_error(monkeypatch) -> None:
    monkeypatch.setitem(pipeline.STEP_HANDLERS, "publish", lambda: (_ for _ in ()).throw(RuntimeError("publish failed")))

    with pytest.raises(RuntimeError, match="publish failed"):
        pipeline.run_selected_steps(["publish"])


def test_run_selected_steps_collects_failures_when_continue_on_error_enabled(monkeypatch) -> None:
    called_steps: list[str] = []

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "build", lambda: called_steps.append("build"))

    def failing_publish() -> None:
        called_steps.append("publish")
        raise RuntimeError("publish failed")

    monkeypatch.setitem(pipeline.STEP_HANDLERS, "publish", failing_publish)

    with pytest.raises(RuntimeError, match="Pipeline finalizado com falhas nas etapas: publish"):
        pipeline.run_selected_steps(["build", "publish"], continue_on_error=True)

    assert called_steps == ["build", "publish"]
