from __future__ import annotations

import pandas as pd

from src.privacy_transformations import (
    apply_privacy_actions,
    generalize_date_to_year,
    hash_value,
    mask_cnpj,
    mask_cpf,
    mask_email,
    mask_phone,
)


def test_masking_helpers() -> None:
    assert mask_email("alice@example.com").startswith("a***@")
    assert mask_cpf("123.456.789-09").endswith("-09")
    assert mask_cnpj("12.345.678/0001-99").endswith("-99")
    assert mask_phone("+55 11 99999-0000").endswith("0000")
    assert len(hash_value("secret")) == 64
    assert generalize_date_to_year("2024-05-01") == "2024"


def test_apply_privacy_actions() -> None:
    df = pd.DataFrame(
        {
            "email": ["alice@example.com"],
            "cpf": ["123.456.789-09"],
            "order_date": ["2025-01-10"],
            "notes": ["internal"],
        }
    )
    classification_df = pd.DataFrame(
        {
            "column_name": ["email", "cpf", "order_date", "notes"],
            "recommended_action": ["mask", "remove", "anonymize", "review"],
        }
    )
    transformed, metadata = apply_privacy_actions(df, classification_df)
    assert "cpf" not in transformed.columns
    assert transformed.loc[0, "email"].startswith("a***@")
    assert transformed.loc[0, "order_date"] == "2025"
    assert "review" in metadata["action"].tolist()
