from __future__ import annotations

from typing import Literal, TypedDict

DataQualityStatus = Literal["PASS", "FAIL"]
DataQualitySeverity = Literal["low", "medium", "high", "critical"]
LGPDClassification = Literal[
    "non_personal",
    "personal_data",
    "sensitive_personal_data",
    "indirect_identifier",
]
RiskLevel = Literal["low", "medium", "high"]
RecommendedAction = Literal["keep", "mask", "anonymize", "remove", "review"]
PublicationRecommendation = Literal["approved", "needs_review", "blocked"]
FreshnessStatus = Literal["fresh", "warning", "stale", "unknown"]


class DataQualityCheck(TypedDict):
    check_name: str
    status: str
    severity: str
    affected_columns: str
    affected_rows: int
    recommendation: str
    rule_source: str


class DataQualityResult(TypedDict):
    total_rows: int
    total_columns: int
    null_pct_by_column: dict[str, float]
    columns_over_30pct_null: list[str]
    duplicate_rows: int
    dtypes: dict[str, str]
    cardinality: dict[str, int]
    possible_unique_keys: list[str]
    constant_columns: list[str]
    checks: list[DataQualityCheck]
    failed_checks_count: int


class PrivacyRiskResult(TypedDict):
    score: int
    total_score: int
    risk_level: RiskLevel
    explanation: str
    summary: str
    components: dict[str, int]
    score_components: dict[str, int]
    per_component_points: dict[str, int]
    component_explanations: dict[str, str]
    publication_recommendation: PublicationRecommendation
    recommendations: list[str]
