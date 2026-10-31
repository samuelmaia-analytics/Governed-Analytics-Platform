from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from app.i18n import LOCALE_EN_US, Locale

COHORT_SLICE_PATH = Path("data/published/semantic/cohort_slice.csv")


def _load_cohort_slice() -> pd.DataFrame:
    if not COHORT_SLICE_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(COHORT_SLICE_PATH)


def _format_decimal(value: int | float, decimal_places: int) -> str:
    if pd.isna(value):
        return "—"
    numeric_value = float(value)
    formatted = f"{numeric_value:,.{decimal_places}f}"
    return formatted.replace(",", "_").replace(".", ",").replace("_", ".")


def _format_integer(value: int | float) -> str:
    return f"{int(float(value)):,}".replace(",", ".")


def _format_percentage(value: int | float) -> str:
    formatted = _format_decimal(value, 1)
    return formatted if formatted == "—" else f"{formatted}%"


def _format_currency(value: int | float) -> str:
    formatted = _format_decimal(value, 2)
    return formatted if formatted == "—" else f"R$ {formatted}"


def _format_month_offset(value: int | float) -> str:
    return f"Mês {int(float(value))}"


def render_cohort_retention(locale: Locale) -> None:
    is_en = locale == LOCALE_EN_US
    st.title("Retenção de Clientes")
    st.subheader(
        "Análise por cohorts para acompanhar a permanência de clientes ao longo "
        "dos meses após a primeira compra."
    )
    st.caption(
        "A retenção compara, em cada cohort, a quantidade de clientes de cada mês "
        "relativo com o volume do mês inicial."
    )
    st.markdown("### Como interpretar esta página")
    st.write(
        "Cada linha representa um grupo mensal de clientes e cada coluna representa "
        "o número de meses desde a primeira compra. O Mês 0 é o baseline de cada "
        "grupo e serve como denominador para o cálculo de retenção."
    )
    st.caption(
        "Células vazias podem representar combinações inexistentes ou ausência de "
        "baseline disponível no artefato persistido."
    )
    st.markdown(
        "**Retenção = clientes no mês relativo ÷ clientes do Mês 0 × 100**"
    )

    cohort_df = _load_cohort_slice()
    required = {
        "purchase_cohort_month",
        "cohort_order_month_number",
        "customers",
        "avg_ticket",
    }
    if cohort_df.empty or not required.issubset(cohort_df.columns):
        st.info(
            "Dados de retenção não disponíveis neste ambiente."
            if not is_en
            else "Retention data is unavailable in this environment."
        )
        st.caption(
            "A visualização depende do slice semântico de cohorts persistido por "
            "uma execução controlada."
            if not is_en
            else "This view depends on the persisted semantic cohort slice."
        )
        return

    cohort_df = cohort_df.copy()
    cohort_df["purchase_cohort_month"] = cohort_df["purchase_cohort_month"].astype(str)
    cohort_df["cohort_order_month_number"] = pd.to_numeric(
        cohort_df["cohort_order_month_number"], errors="coerce"
    ).fillna(0)

    baseline = cohort_df[cohort_df["cohort_order_month_number"] == 0][
        ["purchase_cohort_month", "customers"]
    ].rename(columns={"customers": "baseline_customers"})
    retention = cohort_df.merge(baseline, on="purchase_cohort_month", how="left")
    retention["retention_rate"] = (
        retention["customers"] / retention["baseline_customers"].replace(0, pd.NA)
    ) * 100

    valid_baseline = retention["baseline_customers"].notna() & retention[
        "baseline_customers"
    ].ne(0)
    cohort_count = int(
        retention.loc[valid_baseline, "purchase_cohort_month"].nunique()
    )
    period_start = str(cohort_df["purchase_cohort_month"].min())
    period_end = str(cohort_df["purchase_cohort_month"].max())
    relative_month_count = int(cohort_df["cohort_order_month_number"].nunique())
    calculable_cells = int(retention["retention_rate"].notna().sum())

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Cohorts analisados", _format_integer(cohort_count))
    metric_2.metric("Período analisado", f"{period_start} a {period_end}")
    metric_3.metric(
        "Meses relativos observados", _format_integer(relative_month_count)
    )
    metric_4.metric(
        "Células com retenção calculável", _format_integer(calculable_cells)
    )

    st.markdown("### Leitura executiva")
    st.markdown(
        f"- A análise reúne **{_format_integer(cohort_count)} cohorts mensais**.\n"
        f"- O período observado vai de **{period_start} a {period_end}**.\n"
        f"- Há **{_format_integer(relative_month_count)} meses relativos** "
        "representados.\n"
        f"- Foram calculadas **{_format_integer(calculable_cells)} células de "
        "retenção**."
    )

    retention_pivot = retention.pivot_table(
        index="purchase_cohort_month",
        columns="cohort_order_month_number",
        values="retention_rate",
        aggfunc="mean",
    )
    retention_text = retention_pivot.map(_format_percentage)
    retention_offsets = list(retention_pivot.columns)
    retention_offset_labels = [
        _format_month_offset(value) for value in retention_offsets
    ]
    fig_retention = px.imshow(
        retention_pivot,
        text_auto=False,
        aspect="auto",
        color_continuous_scale="Teal",
        title="Matriz de retenção por cohort (%)",
        labels={
            "x": "Meses desde a primeira compra",
            "y": "Cohort de compra",
            "color": "Retenção (%)",
        },
    )
    fig_retention.update_traces(
        text=retention_text.to_numpy(),
        customdata=[retention_offset_labels for _ in retention_pivot.index],
        texttemplate="%{text}",
        hovertemplate=(
            "Cohort: %{y}<br>%{customdata}<br>Retenção: %{text}<extra></extra>"
        ),
    )
    fig_retention.update_xaxes(
        tickmode="array",
        tickvals=retention_offsets,
        ticktext=retention_offset_labels,
        title_text="Meses desde a primeira compra",
    )
    fig_retention.update_yaxes(title_text="Cohort de compra")

    ticket_pivot = cohort_df.pivot_table(
        index="purchase_cohort_month",
        columns="cohort_order_month_number",
        values="avg_ticket",
        aggfunc="mean",
    )
    ticket_text = ticket_pivot.map(_format_currency)
    ticket_offsets = list(ticket_pivot.columns)
    ticket_offset_labels = [_format_month_offset(value) for value in ticket_offsets]
    fig_ticket = px.imshow(
        ticket_pivot,
        text_auto=False,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Ticket médio por cohort",
        labels={
            "x": "Meses desde a primeira compra",
            "y": "Cohort de compra",
            "color": "Ticket médio",
        },
    )
    fig_ticket.update_traces(
        text=ticket_text.to_numpy(),
        customdata=[ticket_offset_labels for _ in ticket_pivot.index],
        texttemplate="%{text}",
        hovertemplate=(
            "Cohort: %{y}<br>%{customdata}<br>Ticket médio: %{text}<extra></extra>"
        ),
    )
    fig_ticket.update_xaxes(
        tickmode="array",
        tickvals=ticket_offsets,
        ticktext=ticket_offset_labels,
        title_text="Meses desde a primeira compra",
    )
    fig_ticket.update_yaxes(title_text="Cohort de compra")

    retention_tab, ticket_tab = st.tabs(["Retenção", "Ticket médio"])
    with retention_tab:
        st.plotly_chart(fig_retention, width="stretch")
    with ticket_tab:
        st.plotly_chart(fig_ticket, width="stretch")

    technical_table = retention[
        [
            "purchase_cohort_month",
            "cohort_order_month_number",
            "customers",
            "baseline_customers",
            "retention_rate",
            "avg_ticket",
        ]
    ].sort_values(["purchase_cohort_month", "cohort_order_month_number"])

    executive_table = technical_table[
        [
            "purchase_cohort_month",
            "cohort_order_month_number",
            "customers",
            "retention_rate",
            "avg_ticket",
        ]
    ].copy()
    executive_table["cohort_order_month_number"] = executive_table[
        "cohort_order_month_number"
    ].map(_format_month_offset)
    executive_table["customers"] = executive_table["customers"].map(_format_integer)
    executive_table["retention_rate"] = executive_table["retention_rate"].map(
        _format_percentage
    )
    executive_table["avg_ticket"] = executive_table["avg_ticket"].map(
        _format_currency
    )
    executive_table = executive_table.rename(
        columns={
            "purchase_cohort_month": "Cohort",
            "cohort_order_month_number": "Mês relativo",
            "customers": "Clientes",
            "retention_rate": "Retenção",
            "avg_ticket": "Ticket médio",
        }
    )

    st.markdown("### Detalhamento por cohort")
    st.dataframe(
        executive_table,
        width="stretch",
        hide_index=True,
    )

    with st.expander("Detalhes técnicos da retenção", expanded=False):
        st.caption(
            "Os valores técnicos abaixo preservam os identificadores e cálculos "
            "usados na lógica analítica."
        )
        st.dataframe(technical_table, width="stretch", hide_index=True)
