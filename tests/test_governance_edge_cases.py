from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import risk_scoring
from src.data_quality import run_data_quality_checks
from src.governance_history import (
    _compute_warning_and_critical_failures,
    append_governance_history_from_dataframes,
)
from src.lgpd_classifier import (
    classify_dataframe_columns,
    load_classification_contract,
    map_risk_and_action,
)
from src.privacy_transformations import (
    apply_privacy_actions,
    generalize_date_to_year,
    mask_cnpj,
    mask_cpf,
    mask_phone,
)
from src.publication_gate import evaluate_publication_readiness
from src.report_generator import _markdown_table


def test_publication_gate_high_privacy_risk_escalates_severity() -> None:
    result = evaluate_publication_readiness(
        data_quality_score=95,
        privacy_risk_score=80,
        critical_rule_failures=0,
        freshness_status="fresh",
        schema_contract_status="passed",
        has_sensitive_data_without_protection=False,
    )
    assert result.decision == "Needs Review"
    assert result.severity == "High"


def test_data_quality_without_default_yaml_rules(monkeypatch: object) -> None:
    df = pd.DataFrame({"id": [1, 2], "metric": [10, 12]})
    monkeypatch.setattr(Path, "exists", lambda self: False)  # type: ignore[arg-type]
    result = run_data_quality_checks(df)
    assert all(check["rule_source"] == "built_in" for check in result["checks"])


def test_lgpd_load_contract_none_and_missing_path() -> None:
    empty_contract = load_classification_contract(None)
    assert empty_contract.exact == {}
    missing_contract = load_classification_contract(
        Path("contracts/governance/does_not_exist.yml")
    )
    assert missing_contract.exact == {}


def test_lgpd_contract_contains_and_regex_rules(tmp_path: Path) -> None:
    contract_path = tmp_path / "rules.yml"
    contract_path.write_text(
        "\n".join(
            [
                "column_rules:",
                "  contains:",
                "    - token: user_",
                "      lgpd_classification: personal_data",
                "      risk_level: high",
                "      recommended_action: mask",
                "      reason: Contains user_",
                "  regex:",
                "    - pattern: '^.*_token$'",
                "      lgpd_classification: sensitive_personal_data",
                "      risk_level: high",
                "      recommended_action: anonymize",
                "      reason: Regex token rule",
            ]
        ),
        encoding="utf-8",
    )
    df = pd.DataFrame({"user_name": ["ana"], "session_token": ["abc123"]})
    result = classify_dataframe_columns(df, contract_path=contract_path)
    row_user = result.loc[result["column_name"] == "user_name"].iloc[0]
    row_token = result.loc[result["column_name"] == "session_token"].iloc[0]
    assert row_user["recommended_action"] == "mask"
    assert row_token["recommended_action"] == "anonymize"


def test_lgpd_map_risk_sensitive_biometric_and_personal_document() -> None:
    risk_sensitive, action_sensitive = map_risk_and_action(
        "sensitive_personal_data", "biometric_hash"
    )
    risk_personal, action_personal = map_risk_and_action(
        "personal_data", "documento_cliente"
    )
    assert (risk_sensitive, action_sensitive) == ("high", "remove")
    assert (risk_personal, action_personal) == ("high", "remove")


def test_privacy_transformations_invalid_values_and_hash_anonymization() -> None:
    assert mask_cpf("123") == "***.***.***-**"
    assert mask_cnpj("123") == "**.***.***/****-**"
    assert mask_phone("12") == "****"
    assert generalize_date_to_year("not-a-date") == "unknown_year"

    df = pd.DataFrame({"free_text": ["secret-1"], "present_col": ["ok"]})
    classification_df = pd.DataFrame(
        {
            "column_name": ["free_text", "missing_col", "present_col"],
            "recommended_action": ["anonymize", "remove", "keep"],
        }
    )
    transformed, metadata = apply_privacy_actions(df, classification_df)
    assert transformed.loc[0, "free_text"] != "secret-1"
    assert "missing_col" not in transformed.columns
    assert "keep" in metadata["action"].tolist()


def test_governance_history_failure_counter_and_append_from_dataframes(
    tmp_path: Path,
) -> None:
    assert _compute_warning_and_critical_failures({"checks": "invalid"}) == (0, 0)  # type: ignore[arg-type]

    quality_result = {
        "total_rows": 2,
        "total_columns": 2,
        "null_pct_by_column": {"a": 0.0},
        "columns_over_30pct_null": [],
        "duplicate_rows": 0,
        "dtypes": {},
        "cardinality": {},
        "possible_unique_keys": [],
        "constant_columns": [],
        "checks": [
            {"check_name": "ok", "status": "PASS", "severity": "low"},
            "skip-me",
        ],
        "failed_checks_count": 0,
    }
    df = pd.DataFrame({"customer_email": ["a@x.com", "b@x.com"], "v": [1, 2]})
    classification_df = pd.DataFrame(
        {
            "column_name": ["customer_email", "v"],
            "lgpd_classification": ["personal_data", "non_personal"],
        }
    )
    output = tmp_path / "history.csv"
    path = append_governance_history_from_dataframes(
        df=df,
        classification_df=classification_df,
        quality_result=quality_result,
        publication_status="Approved",
        history_path=output,
    )
    stored = pd.read_csv(path)
    assert "privacy_risk_score" in stored.columns
    assert int(stored["failed_rules_count"].iloc[0]) == 0


def test_risk_scoring_coercion_and_null_penalty_paths() -> None:
    class IntLike:
        def __int__(self) -> int:
            return 3

    assert risk_scoring._coerce_int(4.7) == 4
    assert risk_scoring._coerce_int("9") == 9
    assert risk_scoring._coerce_int("bad") == 0
    assert risk_scoring._coerce_int(IntLike()) == 3

    classification_df = pd.DataFrame(
        {
            "column_name": ["customer_email", "health_flag"],
            "lgpd_classification": ["personal_data", "sensitive_personal_data"],
            "null_pct": [50.0, 30.0],
        }
    )
    result = risk_scoring.calculate_privacy_risk_score(
        classification_df, total_rows=100
    )
    assert result["score_components"]["critical_null_penalty"] > 0


def test_report_generator_markdown_table_empty() -> None:
    assert _markdown_table(pd.DataFrame()) == "_No data available._"
