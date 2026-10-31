from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.business_rule_validation as facade
from src.business_rule_components import runners
from src.business_rule_components.models import BusinessRuleResult


def _contract() -> dict:
    return {
        "contract_id": "demo",
        "version": 1,
        "dataset_name": "demo",
        "owner": "owner",
        "rules": [{"rule_id": "r", "type": "range", "severity": "high"}],
    }


def test_runner_wrapper_and_engine_observe_component_and_facade_monkeypatches(
    monkeypatch,
) -> None:
    df = pd.DataFrame({"value": [1]})
    received: list[object] = []

    def fake_runner(received_df, rule):
        received.extend([received_df, rule])
        return pd.Series([False])

    monkeypatch.setattr(runners, "rule_range", fake_runner)
    direct = facade._rule_range(df, {"rule_id": "direct"})
    monkeypatch.setattr(facade, "_rule_range", fake_runner)
    results = facade.run_business_rules(df, _contract())

    assert direct.tolist() == [False]
    assert received[0] is df
    assert results == [BusinessRuleResult("r", "PASS", "high", 0, 0.0, "")]


def test_output_wrappers_use_live_facade_paths(tmp_path: Path, monkeypatch) -> None:
    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    results_path = quality_dir / "results.csv"
    report_path = docs_dir / "report.md"
    results = [BusinessRuleResult("r", "PASS", "high", 0, 0.0, "")]
    contract = _contract()
    captured: dict[str, object] = {}

    monkeypatch.setattr(facade, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(facade, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(facade, "RESULTS_PATH", results_path)
    monkeypatch.setattr(facade, "REPORT_PATH", report_path)
    monkeypatch.setattr(
        facade._outputs,
        "save_results",
        lambda value, **kwargs: captured.update(results=(value, kwargs)) or results_path,
    )
    monkeypatch.setattr(
        facade._outputs,
        "save_report",
        lambda value, received_contract, **kwargs: captured.update(
            report=(value, received_contract, kwargs)
        )
        or report_path,
    )
    monkeypatch.setattr(facade._outputs, "render_report", lambda *_args: "markdown")

    assert facade.save_results(results) == results_path
    assert facade.save_report(results, contract) == report_path
    assert facade.render_report(results, contract) == "markdown"
    assert captured["results"][0] is results
    assert captured["results"][1] == {
        "quality_dir": quality_dir,
        "results_path": results_path,
    }
    assert captured["report"][0] is results
    assert captured["report"][1] is contract
    assert captured["report"][2] == {"docs_dir": docs_dir, "report_path": report_path}


def test_main_preserves_order_and_identity(monkeypatch) -> None:
    df = pd.DataFrame({"value": [1]})
    contract = _contract()
    results = [BusinessRuleResult("r", "PASS", "high", 0, 0.0, "")]
    events: list[tuple[str, object | None]] = []
    monkeypatch.setattr(facade, "configure_logging", lambda: None)
    monkeypatch.setattr(facade, "load_fact_table", lambda: events.append(("data", None)) or df)
    monkeypatch.setattr(facade, "load_contract", lambda: events.append(("contract", None)) or contract)
    monkeypatch.setattr(facade, "run_business_rules", lambda a, b: events.append(("run", (a, b))) or results)
    monkeypatch.setattr(facade, "save_results", lambda value: events.append(("results", value)))
    monkeypatch.setattr(facade, "save_report", lambda value, c: events.append(("report", (value, c))))

    facade.main()

    assert [event[0] for event in events] == ["data", "contract", "run", "results", "report"]
    assert events[2][1] == (df, contract)
    assert events[3][1] is results


@pytest.mark.parametrize("failure", ["data", "contract", "run", "results", "report"])
def test_main_propagates_failures_and_stops(failure: str, monkeypatch) -> None:
    events: list[str] = []
    df = pd.DataFrame({"value": [1]})
    contract = _contract()
    results: list[BusinessRuleResult] = []

    def step(name: str, result):
        events.append(name)
        if name == failure:
            raise RuntimeError(f"{name} failed")
        return result

    monkeypatch.setattr(facade, "configure_logging", lambda: None)
    monkeypatch.setattr(facade, "load_fact_table", lambda: step("data", df))
    monkeypatch.setattr(facade, "load_contract", lambda: step("contract", contract))
    monkeypatch.setattr(facade, "run_business_rules", lambda *_args: step("run", results))
    monkeypatch.setattr(facade, "save_results", lambda _value: step("results", None))
    monkeypatch.setattr(facade, "save_report", lambda *_args: step("report", None))

    order = ["data", "contract", "run", "results", "report"]
    with pytest.raises(RuntimeError, match=f"{failure} failed"):
        facade.main()
    assert events == order[: order.index(failure) + 1]


def test_historical_api_remains_available() -> None:
    names = [
        "BusinessRuleResult",
        "load_fact_table",
        "load_contract",
        "_validate_contract_shape",
        "_build_result",
        "_rule_range",
        "_rule_not_null_if",
        "_rule_accepted_values",
        "_rule_compare_columns",
        "_rule_expression",
        "run_business_rules",
        "save_results",
        "render_report",
        "save_report",
        "main",
    ]
    assert all(hasattr(facade, name) for name in names)
    assert all(callable(getattr(facade, name)) for name in names)
