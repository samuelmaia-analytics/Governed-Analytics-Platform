from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import src.schema_contracts as facade
from src.schema_contract_components import discovery
from src.schema_contract_components.models import ContractCheck


def test_discovery_wrappers_observe_component_monkeypatches(tmp_path: Path, monkeypatch) -> None:
    contract_path = tmp_path / "demo.contract.json"
    expected_contract = {"dataset_name": "demo"}
    captured: dict[str, object] = {}

    def fake_load_contract(path: Path) -> dict[str, str]:
        captured["contract_path"] = path
        return expected_contract

    def fake_iter_contract_paths(directory: Path) -> list[Path]:
        captured["contracts_dir"] = directory
        return [contract_path]

    monkeypatch.setattr(
        discovery,
        "load_contract",
        fake_load_contract,
    )
    monkeypatch.setattr(
        discovery,
        "iter_contract_paths",
        fake_iter_contract_paths,
    )
    monkeypatch.setattr(facade, "CONTRACTS_DIR", tmp_path)

    assert facade.load_contract(contract_path) is expected_contract
    assert facade.iter_contract_paths() == [contract_path]
    assert captured == {"contract_path": contract_path, "contracts_dir": tmp_path}


def test_validate_and_runner_preserve_historical_facade_monkeypatches(monkeypatch) -> None:
    df = pd.DataFrame({"id": [1]})
    contract = {
        "dataset_name": "demo",
        "layer": "curated",
        "columns": {"id": "integer"},
    }
    monkeypatch.setattr(facade, "load_dataset", lambda _contract: df)
    validated = facade.validate_contract(contract)
    monkeypatch.setattr(facade, "iter_contract_paths", lambda: [Path("demo.json")])
    monkeypatch.setattr(facade, "load_contract", lambda _path: contract)
    monkeypatch.setattr(facade, "validate_contract", lambda _contract: validated)

    assert facade.run_contract_checks() is not validated
    assert facade.run_contract_checks() == validated


def test_output_wrappers_pass_facade_globals(tmp_path: Path, monkeypatch) -> None:
    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    results_path = quality_dir / "results.csv"
    report_path = docs_dir / "report.md"
    checks = [ContractCheck("demo", "curated", "check", "PASS", "ok")]
    captured: dict[str, object] = {}

    monkeypatch.setattr(facade, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(facade, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(facade, "RESULTS_PATH", results_path)
    monkeypatch.setattr(facade, "REPORT_PATH", report_path)
    monkeypatch.setattr(
        facade._outputs,
        "save_results",
        lambda items, **kwargs: captured.update(results=(items, kwargs)) or results_path,
    )
    monkeypatch.setattr(
        facade._outputs,
        "save_report",
        lambda items, **kwargs: captured.update(report=(items, kwargs)) or report_path,
    )
    monkeypatch.setattr(facade._outputs, "render_report", lambda items: "markdown")

    assert facade.save_results(checks) == results_path
    assert facade.save_report(checks) == report_path
    assert facade.render_report(checks) == "markdown"
    assert captured["results"][0] is checks
    assert captured["results"][1] == {
        "quality_dir": quality_dir,
        "results_path": results_path,
        "logger": facade.LOGGER,
    }
    assert captured["report"][0] is checks
    assert captured["report"][1] == {
        "docs_dir": docs_dir,
        "report_path": report_path,
        "logger": facade.LOGGER,
    }


def test_main_preserves_order_identity_and_error_propagation(monkeypatch) -> None:
    checks = [ContractCheck("demo", "curated", "check", "PASS", "ok")]
    events: list[tuple[str, object | None]] = []
    monkeypatch.setattr(facade, "configure_logging", lambda: None)
    monkeypatch.setattr(
        facade, "run_contract_checks", lambda: events.append(("run", None)) or checks
    )
    monkeypatch.setattr(
        facade, "save_results", lambda value: events.append(("results", value))
    )
    monkeypatch.setattr(
        facade, "save_report", lambda value: events.append(("report", value))
    )

    facade.main()

    assert [event[0] for event in events] == ["run", "results", "report"]
    assert events[1][1] is checks
    assert events[2][1] is checks


@pytest.mark.parametrize(
    ("failure", "expected"),
    [("run", ["run"]), ("results", ["run", "results"]), ("report", ["run", "results", "report"])],
)
def test_main_stops_after_failure(failure: str, expected: list[str], monkeypatch) -> None:
    events: list[str] = []
    checks: list[ContractCheck] = []

    def step(name: str, result):
        events.append(name)
        if name == failure:
            raise RuntimeError(f"{name} failed")
        return result

    monkeypatch.setattr(facade, "configure_logging", lambda: None)
    monkeypatch.setattr(facade, "run_contract_checks", lambda: step("run", checks))
    monkeypatch.setattr(facade, "save_results", lambda _value: step("results", None))
    monkeypatch.setattr(facade, "save_report", lambda _value: step("report", None))

    with pytest.raises(RuntimeError, match=f"{failure} failed"):
        facade.main()
    assert events == expected


def test_historical_api_remains_available() -> None:
    names = [
        "ContractCheck",
        "load_contract",
        "iter_contract_paths",
        "load_dataset",
        "matches_expected_type",
        "validate_contract",
        "run_contract_checks",
        "save_results",
        "render_report",
        "save_report",
        "main",
    ]
    assert all(hasattr(facade, name) for name in names)
    assert all(callable(getattr(facade, name)) for name in names)
