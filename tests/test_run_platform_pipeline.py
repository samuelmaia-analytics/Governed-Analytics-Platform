from __future__ import annotations

from datetime import UTC, datetime

import src.run_platform_pipeline as pipeline
from src.run_platform_pipeline import PIPELINE_STEPS, resolve_steps


def test_resolve_steps_returns_full_pipeline_when_none_provided() -> None:
    steps = resolve_steps(None)

    assert steps == [step.name for step in PIPELINE_STEPS]
    assert "publish" in steps


def test_resolve_steps_preserves_explicit_selection_order() -> None:
    steps = resolve_steps(["build", "quality"])

    assert steps == ["build", "quality"]


def test_list_steps_prints_all_pipeline_steps(capsys) -> None:
    pipeline.list_steps()

    output = capsys.readouterr().out
    assert "- inventory:" in output
    assert "- publish:" in output


def test_main_lists_steps_without_running_pipeline(monkeypatch) -> None:
    calls: list[str] = []

    class Args:
        list_steps = True
        steps = None
        continue_on_error = False

    monkeypatch.setattr(pipeline, "parse_args", lambda: Args())
    monkeypatch.setattr(pipeline, "list_steps", lambda: calls.append("list"))

    pipeline.main()

    assert calls == ["list"]


def test_main_runs_selected_pipeline(monkeypatch) -> None:
    calls: list[str] = []

    class Args:
        list_steps = False
        steps = ["build"]
        continue_on_error = False

    monkeypatch.setattr(pipeline, "parse_args", lambda: Args())
    monkeypatch.setattr(pipeline, "configure_logging", lambda: calls.append("logging"))
    monkeypatch.setattr(type(pipeline.PATHS), "validate", lambda self: calls.append("validate"))
    monkeypatch.setattr(pipeline, "resolve_steps", lambda steps: ["build"] if steps == ["build"] else [])
    monkeypatch.setattr(
        pipeline,
        "run_selected_steps",
        lambda steps, continue_on_error=False: calls.append(f"run:{','.join(steps)}:{continue_on_error}") or [],
    )
    monkeypatch.setattr(
        pipeline,
        "save_pipeline_execution_report",
        lambda selected_steps, executions, metadata: calls.append(f"report:{metadata.run_id}"),
    )
    monkeypatch.setattr(
        pipeline,
        "build_run_metadata",
        lambda started_at, completed_at: pipeline.PipelineRunMetadata(
            run_id="run-test",
            started_at_utc=started_at.isoformat(),
            completed_at_utc=completed_at.isoformat(),
            python_version="3.11.0",
            platform="test-platform",
            git_commit="abc123",
        ),
    )

    pipeline.main()

    assert calls == ["logging", "validate", "run:build:False", "report:run-test"]


def test_build_run_metadata_contains_enterprise_runtime_context(monkeypatch) -> None:
    monkeypatch.setattr(pipeline.platform, "python_version", lambda: "3.11.9")
    monkeypatch.setattr(pipeline.platform, "platform", lambda: "Windows-Enterprise")
    monkeypatch.setattr(pipeline, "resolve_git_commit", lambda: "deadbee")

    metadata = pipeline.build_run_metadata(
        datetime(2026, 3, 31, 10, 0, tzinfo=UTC),
        datetime(2026, 3, 31, 10, 5, tzinfo=UTC),
    )

    assert metadata.run_id == "run-20260331T100000Z"
    assert metadata.python_version == "3.11.9"
    assert metadata.platform == "Windows-Enterprise"
    assert metadata.git_commit == "deadbee"
