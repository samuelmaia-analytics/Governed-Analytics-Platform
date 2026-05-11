from __future__ import annotations

from datetime import date

import pandas as pd

from src.governance_types import DataQualityResult, PrivacyRiskResult


def build_treatment_inventory(
    dataset_name: str = "fact_orders_dashboard",
) -> pd.DataFrame:
    rows = [
        {
            "dataset": dataset_name,
            "process_name": "Executive analytics publication",
            "data_subjects": "e-commerce customers and sellers (synthetic/public context)",
            "personal_data_categories": "indirect identifiers, contact-like fields, transactional metadata",
            "purpose": "Executive performance and governance monitoring",
            "legal_basis": "legitimate_interest (simulated)",
            "controller": "Olist Governed Analytics (fictitious)",
            "operator": "Analytics Platform Team (fictitious)",
            "dpo": "dpo@example.org (fictitious)",
            "retention_policy": "12 months in published layer, 24 months in curated internal layer (simulated)",
            "sharing_scope": "internal executive consumption only",
        }
    ]
    return pd.DataFrame(rows)


def build_risk_matrix(
    classification_df: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_result: DataQualityResult,
) -> pd.DataFrame:
    failed_checks = int(quality_result["failed_checks_count"])
    sensitive_count = int(
        (classification_df["lgpd_classification"] == "sensitive_personal_data").sum()
    )
    personal_count = int(
        (classification_df["lgpd_classification"] == "personal_data").sum()
    )
    indirect_count = int(
        (classification_df["lgpd_classification"] == "indirect_identifier").sum()
    )

    rows = [
        {
            "risk_id": "R1",
            "risk_event": "Leakage of direct or sensitive identifiers",
            "probability": "High" if sensitive_count > 0 else "Medium",
            "impact": "High",
            "severity": "Critical" if risk_result["risk_level"] == "high" else "High",
            "mitigation": "Pseudonymize/remove sensitive fields before publication.",
            "evidence": "Classification inventory and publication checks.",
        },
        {
            "risk_id": "R2",
            "risk_event": "Re-identification through quasi-identifiers",
            "probability": "High" if indirect_count >= 3 else "Medium",
            "impact": "Medium",
            "severity": "High" if indirect_count >= 3 else "Medium",
            "mitigation": "Data minimization and aggregation in published layer.",
            "evidence": "Published schema and forbidden-columns validation.",
        },
        {
            "risk_id": "R3",
            "risk_event": "Publication with unresolved quality issues",
            "probability": "High" if failed_checks > 0 else "Low",
            "impact": "Medium",
            "severity": "High" if failed_checks > 0 else "Low",
            "mitigation": "Block/review publication when quality checks fail.",
            "evidence": f"Failed checks count: {failed_checks}.",
        },
        {
            "risk_id": "R4",
            "risk_event": "Missing legal and retention metadata",
            "probability": "Medium",
            "impact": "Medium",
            "severity": "Medium",
            "mitigation": "Maintain processing inventory and LGPD-inspired RIPD sample.",
            "evidence": "Governance docs and treatment inventory.",
        },
        {
            "risk_id": "R5",
            "risk_event": "Overexposure from broad published schema",
            "probability": "Medium" if personal_count > 0 else "Low",
            "impact": "High",
            "severity": "High" if personal_count > 0 else "Medium",
            "mitigation": "Keep published layer minimized to executive use cases.",
            "evidence": "Published contract and schema checks.",
        },
    ]
    return pd.DataFrame(rows)


def generate_ripd_markdown(
    *,
    dataset_name: str,
    treatment_inventory: pd.DataFrame,
    risk_matrix: pd.DataFrame,
    risk_result: PrivacyRiskResult,
    quality_result: DataQualityResult,
) -> str:
    generated_on = date.today().isoformat()
    inventory_row = (
        treatment_inventory.iloc[0].to_dict() if not treatment_inventory.empty else {}
    )
    lines = [
        "# Mini RIPD (LGPD-inspired)",
        "",
        "> Documento simulado para portfólio. Não substitui avaliação jurídica formal.",
        "",
        f"- Data de geração: **{generated_on}**",
        f"- Dataset avaliado: **{dataset_name}**",
        f"- Risco de privacidade: **{risk_result['risk_level']} ({risk_result['score']}/100)**",
        f"- Falhas de qualidade: **{quality_result['failed_checks_count']}**",
        "",
        "## Inventário de Tratamento (simulado)",
        "",
        f"- Finalidade: {inventory_row.get('purpose', '-')}",
        f"- Base legal: {inventory_row.get('legal_basis', '-')}",
        f"- Controlador: {inventory_row.get('controller', '-')}",
        f"- Operador: {inventory_row.get('operator', '-')}",
        f"- Encarregado (DPO): {inventory_row.get('dpo', '-')}",
        f"- Retenção: {inventory_row.get('retention_policy', '-')}",
        "",
        "## Matriz de Risco",
        "",
        "| risk_id | risk_event | probability | impact | severity | mitigation | evidence |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in risk_matrix.itertuples(index=False):
        lines.append(
            f"| {row.risk_id} | {row.risk_event} | {row.probability} | {row.impact} | {row.severity} | {row.mitigation} | {row.evidence} |"
        )

    lines.extend(
        [
            "",
            "## Controles Implementados",
            "",
            "- Classificação de colunas com heurística + contrato YAML.",
            "- Score de risco explicável com recomendação de publicação.",
            "- Checks de qualidade integrados na decisão executiva.",
            "- Camada publicada minimizada e pseudonimizada.",
            "",
            "## Limitações",
            "",
            "- Este RIPD é simulado para demonstração técnica.",
            "- Não representa conformidade jurídica automática com LGPD.",
            "- Requer validação com jurídico e segurança para dados pessoais reais.",
        ]
    )
    return "\n".join(lines)
