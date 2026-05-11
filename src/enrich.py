import pandas as pd


def add_reference_date(
    df: pd.DataFrame, column_name: str = "reference_date"
) -> pd.DataFrame:
    enriched = df.copy()
    enriched[column_name] = pd.Timestamp.utcnow().date()
    return enriched
