from __future__ import annotations

from dataclasses import asdict, fields
from pathlib import Path

import pandas as pd

import src.publish_dashboard as publication

EXPECTED_PRIVACY_CHECKS = [
    "required_columns",
    "forbidden_columns_absent",
    "unexpected_columns",
    "pseudonymized__order_id",
    "pseudonymized__customer_unique_id",
    "pseudonymized__seller_key",
    "default_fill__customer_state",
    "default_fill__seller_state",
    "default_fill__order_status",
    "default_fill__payment_type_mode",
    "default_fill__seller_volume_tier",
    "classification_leakage",
    "policy_required_columns_alignment",
    "policy_forbidden_columns_alignment",
    "policy_pseudonymization_alignment",
    "policy_default_fill_alignment",
]
SYNTHETIC_PRIVACY_GOLDEN_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "privacy_governance_synthetic_4_pass_12_fail.csv"
)


def _source_frame() -> pd.DataFrame:
    data = {
        column: [1]
        for column in publication.PUBLISHED_COLUMNS
        if column != "seller_key"
    }
    data.update(
        {
            "order_id": ["order-1"],
            "order_item_id": [1],
            "customer_unique_id": ["customer-1"],
            "seller_id": ["seller-1"],
            "customer_id": ["raw-customer"],
            "product_id": ["raw-product"],
            "customer_city": ["sao paulo"],
            "order_status": [None],
            "payment_type_mode": [None],
            "seller_volume_tier": [None],
            "customer_state": [None],
            "seller_state": [None],
        }
    )
    return pd.DataFrame(data)


def _current_failing_frame(contract: dict[str, object]) -> pd.DataFrame:
    required = list(contract["required_columns"])  # type: ignore[arg-type]
    columns = [column for column in required if column != "seller_key"]
    frame = pd.DataFrame({column: [pd.NA] for column in columns})
    frame["order_id"] = "raw-order"
    frame["customer_unique_id"] = "raw-customer-unique"
    frame["customer_city"] = "sao paulo"
    frame["customer_id"] = "raw-customer"
    frame["product_id"] = "raw-product"
    frame["seller_id"] = "raw-seller"
    return frame


def test_privacy_result_models_and_pseudonymization_are_stable(tmp_path: Path) -> None:
    token = publication.pseudonymize("abc", "order_id")

    assert token == "order_id_6fb07f174b0fea0e"
    assert publication.pseudonymize("abc", "order_id") == token
    assert publication.pseudonymize(pd.NA, "order_id") is pd.NA
    assert [field.name for field in fields(publication.PrivacyCheck)] == [
        "check_name",
        "status",
        "details",
    ]
    assert [field.name for field in fields(publication.PublishedArtifacts)] == [
        "parquet_path",
        "csv_path",
        "rows",
        "columns",
    ]
    artifacts = publication.PublishedArtifacts(
        tmp_path / "published.parquet", tmp_path / "published.csv", 1, 34
    )
    assert asdict(artifacts)["columns"] == 34


def test_published_schema_minimization_pseudonymization_and_defaults() -> None:
    published = publication.build_published_dashboard_table(_source_frame())

    assert list(published.columns) == publication.PUBLISHED_COLUMNS
    assert published.shape == (1, 34)
    assert set(publication.REMOVED_SENSITIVE_COLUMNS).isdisjoint(published.columns)
    assert published.at[0, "order_id"].startswith("order_id_")
    assert published.at[0, "customer_unique_id"].startswith("customer_unique_id_")
    assert published.at[0, "seller_key"].startswith("seller_id_")
    assert "seller_id" not in published.columns
    assert published.loc[0, ["customer_state", "seller_state"]].tolist() == [
        "NA",
        "NA",
    ]
    assert published.loc[0, ["order_status", "payment_type_mode"]].tolist() == [
        "unknown",
        "unknown",
    ]
    assert published.at[0, "seller_volume_tier"] == "long_tail"


def test_privacy_checks_match_synthetic_4_pass_12_fail_golden() -> None:
    contract = publication.load_privacy_contract()
    policy = publication.load_domain_policy(contract)
    checks = publication.validate_privacy_controls(
        _current_failing_frame(contract), contract, policy
    )
    golden = pd.read_csv(SYNTHETIC_PRIVACY_GOLDEN_PATH)

    assert [check.check_name for check in checks] == EXPECTED_PRIVACY_CHECKS
    assert [check.status for check in checks].count("PASS") == 4
    assert [check.status for check in checks].count("FAIL") == 12
    assert [asdict(check) for check in checks] == golden.to_dict("records")


def test_run_publish_dashboard_writes_only_to_isolated_paths(
    tmp_path: Path, monkeypatch
) -> None:
    published_dir = tmp_path / "published"
    quality_dir = tmp_path / "quality"
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(publication, "PUBLISHED_DASHBOARD_DIR", published_dir)
    monkeypatch.setattr(publication, "QUALITY_DIR", quality_dir)
    monkeypatch.setattr(publication, "DOCS_DIR", docs_dir)
    monkeypatch.setattr(
        publication, "PUBLISHED_PARQUET_PATH", published_dir / "dashboard.parquet"
    )
    monkeypatch.setattr(
        publication, "PUBLISHED_CSV_PATH", published_dir / "dashboard.csv"
    )
    monkeypatch.setattr(
        publication, "PRIVACY_RESULTS_PATH", quality_dir / "privacy.csv"
    )
    monkeypatch.setattr(publication, "REPORT_PATH", docs_dir / "privacy.md")
    source = _source_frame()
    monkeypatch.setattr(publication, "load_internal_fact", lambda: source)

    artifacts = publication.run_publish_dashboard()

    assert artifacts == publication.PublishedArtifacts(
        published_dir / "dashboard.parquet",
        published_dir / "dashboard.csv",
        1,
        34,
    )
    assert all(
        path.exists()
        for path in (
            artifacts.parquet_path,
            artifacts.csv_path,
            quality_dir / "privacy.csv",
            docs_dir / "privacy.md",
        )
    )
    assert set(pd.read_csv(quality_dir / "privacy.csv")["status"]) == {"PASS"}
