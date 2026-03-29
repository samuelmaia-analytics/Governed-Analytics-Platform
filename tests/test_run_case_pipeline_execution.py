from __future__ import annotations

import src.run_case_pipeline as pipeline


def test_run_selected_steps_executes_requested_functions_in_order(monkeypatch) -> None:
    called_steps: list[str] = []

    monkeypatch.setattr(pipeline, "run_inventory", lambda: called_steps.append("inventory"))
    monkeypatch.setattr(pipeline, "run_build", lambda: called_steps.append("build"))
    monkeypatch.setattr(pipeline, "run_publish_dashboard", lambda: called_steps.append("publish"))

    pipeline.run_selected_steps(["inventory", "build", "publish"])

    assert called_steps == ["inventory", "build", "publish"]


def test_run_selected_steps_executes_semantic_and_monitor_steps(monkeypatch) -> None:
    called_steps: list[str] = []

    monkeypatch.setattr(pipeline, "run_semantic_layer", lambda: called_steps.append("semantic"))
    monkeypatch.setattr(pipeline, "run_monitoring", lambda: called_steps.append("monitor") or ["ok"])
    monkeypatch.setattr(pipeline, "save_published_monitoring_results", lambda results: called_steps.append("save_results"))
    monkeypatch.setattr(pipeline, "save_published_monitoring_report", lambda results: called_steps.append("save_report"))

    pipeline.run_selected_steps(["semantic", "monitor"])

    assert called_steps == ["semantic", "monitor", "save_results", "save_report"]


def test_run_selected_steps_executes_quality_flow(monkeypatch) -> None:
    called_steps: list[str] = []

    monkeypatch.setattr(pipeline, "load_fact_table", lambda: "fact_df")
    monkeypatch.setattr(
        pipeline,
        "run_quality_checks",
        lambda df: called_steps.append(f"quality_checks:{df}") or ["quality_result"],
    )
    monkeypatch.setattr(
        pipeline,
        "save_quality_results",
        lambda results: called_steps.append(f"save_results:{results[0]}"),
    )
    monkeypatch.setattr(
        pipeline,
        "save_quality_report",
        lambda df, results: called_steps.append(f"save_report:{df}:{results[0]}"),
    )

    pipeline.run_selected_steps(["quality"])

    assert called_steps == [
        "quality_checks:fact_df",
        "save_results:quality_result",
        "save_report:fact_df:quality_result",
    ]


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

    monkeypatch.setattr(pipeline, "parse_args", lambda: Args())
    monkeypatch.setattr(pipeline, "list_steps", lambda: calls.append("list"))

    pipeline.main()

    assert calls == ["list"]


def test_main_runs_selected_pipeline(monkeypatch) -> None:
    calls: list[str] = []

    class Args:
        list_steps = False
        steps = ["build"]

    monkeypatch.setattr(pipeline, "parse_args", lambda: Args())
    monkeypatch.setattr(pipeline, "configure_logging", lambda: calls.append("logging"))
    monkeypatch.setattr(pipeline, "resolve_steps", lambda steps: ["build"] if steps == ["build"] else [])
    monkeypatch.setattr(pipeline, "run_selected_steps", lambda steps: calls.append(f"run:{','.join(steps)}") or [])
    monkeypatch.setattr(pipeline, "save_pipeline_execution_report", lambda selected_steps, executions: calls.append("report"))

    pipeline.main()

    assert calls == ["logging", "run:build", "report"]
