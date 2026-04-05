from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from streamlit_app.analytics import (
    build_executive_insights,
    build_filter_context_summary,
    build_regional_insights,
    build_smart_summary,
    build_state_table,
)
from streamlit_app.charts import (
    chart_category_share_donut,
    chart_category_value_vs_satisfaction,
    chart_delay_by_category,
    chart_delay_by_period,
    chart_delivery_boxplot,
    chart_delivery_vs_review,
    chart_orders_area,
    chart_revenue_line,
    chart_seasonality_heatmap,
    chart_state_delay_rate,
    chart_state_delivery_time,
    chart_state_revenue,
    chart_top_categories_orders,
    chart_top_categories_revenue,
)
from streamlit_app.data import FilterState
from streamlit_app.formatting import (
    format_currency,
    format_date_label,
    format_number,
    format_pct,
    get_format_locale,
    to_csv_bytes,
)
from streamlit_app.theme import COLORS


def t(pt_br: str, en_us: str) -> str:
    if get_format_locale() == "en-US":
        return en_us
    return pt_br


def build_health_recommendation(main_risk: str, failed_checks: int) -> str:
    if failed_checks == 0:
        return t(
            "Nenhuma ação imediata é necessária. Manter a cadência de publicação e monitoramento.",
            "No immediate action is required. Keep the publication and monitoring cadence.",
        )
    risk_map = {
        "published_file_freshness_hours": t(
            "Regenerar a camada publicada e confirmar atualização do artefato oficial antes de nova leitura executiva.",
            "Regenerate the published layer and confirm the official artifact timestamp before the next executive readout.",
        ),
        "published_row_count": t(
            "Validar a publicação recente e revisar se houve corte indevido de volume na camada oficial.",
            "Validate the latest publication and review whether the official layer lost unexpected volume.",
        ),
        "published_missing_required_columns": t(
            "Comparar schema publicado com o contrato e bloquear consumo até restaurar as colunas obrigatórias.",
            "Compare the published schema with the contract and block consumption until required columns are restored.",
        ),
        "published_anomaly__revenue_gross_latest_month_delta_pct": t(
            "Revisar variação de receita no último mês e confirmar se o desvio é negócio ou incidente de publicação.",
            "Review the latest-month revenue change and confirm whether the shift is business-driven or a publication issue.",
        ),
        "published_anomaly__orders_latest_month_delta_pct": t(
            "Checar volume de pedidos do último mês e validar se a queda ou salto veio da fonte ou da publicação.",
            "Check latest-month order volume and validate whether the shift came from the source or the publication process.",
        ),
        "published_anomaly__delay_rate_latest_month_delta_pct_points": t(
            "Investigar a taxa de atraso do último mês em nível de pedido e revisar impacto regional ou logístico.",
            "Investigate the latest-month delay rate at order level and review regional or logistics impact.",
        ),
    }
    return risk_map.get(
        main_risk,
        t(
            "Abrir o runbook de incidente, validar a causa raiz e confirmar se o problema afeta a camada publicada ou apenas ativos derivados.",
            "Open the incident runbook, validate the root cause, and confirm whether the issue affects the published layer or only derived assets.",
        ),
    )


def metric_card(label: str, value: str, delta: str, help_text: str, delta_color: str = "normal") -> None:
    st.metric(label=label, value=value, delta=delta, help=help_text, delta_color=delta_color)


def render_header(filters: FilterState, total_rows: int, filtered_rows: int) -> None:
    period_text = f"{format_date_label(filters.start_date)} a {format_date_label(filters.end_date)}"
    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="hero-top">
                <div>
                    <span class="hero-badge">Governed Analytics Platform</span>
                    <h1 class="hero-title">{t("Dashboard Executivo de Receita, Operação e Experiência", "Executive Dashboard for Revenue, Operations and Customer Experience")}</h1>
                    <p class="hero-subtitle">
                        {t(
                            "Painel executivo para leitura rápida de receita, categorias, operação e experiência do cliente, transformando o dataset Olist em uma camada analítica pronta para decisão.",
                            "Executive interface for fast reading of revenue, category, operations and customer experience signals, turning the Olist dataset into a decision-ready analytics product.",
                        )}
                    </p>
                </div>
                <div class="hero-badge">{t("Dataset Olist | Brazilian E-Commerce Public Dataset", "Olist Dataset | Brazilian E-Commerce Public Dataset")}</div>
            </div>
            <div class="hero-dataset">
                <div class="hero-stat">
                    <strong>{t("Objetivo analítico", "Analytics objective")}</strong>
                    {t("Entender onde o negócio cresce, onde perde eficiência e onde estão as prioridades operacionais.", "Understand where the business grows, where it loses efficiency, and where operational priorities sit.")}
                </div>
                <div class="hero-stat">
                    <strong>{t("Leitura atual", "Current view")}</strong>
                    {t("Recorte ativo de", "Active slice from")} {period_text}, {t("com", "with")} {format_number(filtered_rows)} {t("registros filtrados refletidos em indicadores, visuais e insights.", "filtered records reflected in KPIs, visuals and insights.")}
                </div>
                <div class="hero-stat">
                    <strong>{t("Base executiva", "Executive base")}</strong>
                    {t("Consumo governado a partir de <code>fact_orders_dashboard</code> e ativos semânticos publicados, com", "Governed consumption from <code>fact_orders_dashboard</code> and published semantic assets, with")} {format_number(total_rows)} {t("registros disponíveis para análise.", "records available for analysis.")}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(eyebrow: str, title: str, copy: str) -> None:
    st.markdown("<div class='section-shell'>", unsafe_allow_html=True)
    st.markdown(f"<div class='section-eyebrow'>{eyebrow}</div>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='section-title'>{title}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='section-copy'>{copy}</p>", unsafe_allow_html=True)


def close_section() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_row(metrics: list[dict[str, str]]) -> None:
    st.markdown(
        """
            <div class="kpi-shell">
            <div class="section-eyebrow">{t("KPI Layer", "KPI Layer")}</div>
            <h2 class="section-title">{t("Indicadores principais do recorte", "Primary metrics for the selected slice")}</h2>
            <p class="section-copy">
                {t(
                    "Os KPIs abaixo resumem escala comercial, monetização, satisfação e eficiência operacional, com comparação contra o período imediatamente anterior quando houver base.",
                    "The KPIs below summarize commercial scale, monetization, satisfaction and operational efficiency, with a comparison against the immediately previous period when available.",
                )}
            </p>
        """,
        unsafe_allow_html=True,
    )
    row1 = st.columns(4, gap="medium")
    row2 = st.columns(4, gap="medium")
    for idx, metric in enumerate(metrics[:4]):
        with row1[idx]:
            metric_card(metric["label"], metric["value"], metric["delta"], metric["help"], metric.get("delta_color", "normal"))
    for idx, metric in enumerate(metrics[4:8]):
        with row2[idx]:
            metric_card(metric["label"], metric["value"], metric["delta"], metric["help"], metric.get("delta_color", "normal"))
    st.markdown("</div>", unsafe_allow_html=True)


def render_context_bar(df: pd.DataFrame, filters: FilterState) -> None:
    items = build_filter_context_summary(df, filters)
    items_html = "".join(f"<div class='hero-stat'><strong>{label}</strong>{value}</div>" for label, value in items)
    st.markdown(
        f"""
        <div class="section-shell" style="padding:0.9rem 1rem 0.95rem 1rem;">
            <div class="section-eyebrow">{t("Contexto do Recorte", "Selection Context")}</div>
            <p class="section-copy" style="margin-bottom:0.35rem;">
                {t("Resumo executivo dos filtros ativos para facilitar leitura rápida da sessão atual do dashboard.", "Executive summary of active filters for faster reading of the current dashboard session.")}
            </p>
            <div class="hero-dataset" style="margin-top:0.35rem;">
                {items_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_smart_summary(df: pd.DataFrame) -> None:
    insights = build_smart_summary(df)
    chip_html = "".join(f"<div class='copilot-chip'><strong>{chip['label']}</strong><span>{chip['value']}</span></div>" for chip in insights["chips"])
    rec_html = "".join(f"<li>{item}</li>" for item in insights["recommendations"])
    st.markdown(
        f"""
        <div class="copilot-shell">
            <div class="section-eyebrow">{t("Síntese do Recorte", "Selection Summary")}</div>
            <h2 class="section-title" style="margin-top:0.15rem;">{t("Leitura automática dos principais sinais", "Automatic reading of the main signals")}</h2>
            <p class="section-copy" style="margin-bottom:0.2rem;">{insights["summary"]}</p>
            <div class="copilot-grid">{chip_html}</div>
            <div class="divider-label">{t("Prioridades sugeridas", "Suggested priorities")}</div>
            <ul style="margin:0.3rem 0 0.1rem 1.1rem; color:{COLORS["muted"]}; line-height:1.65;">
                {rec_html}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_regional_kpi(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="regional-kpi">
            <strong>{label}</strong>
            <span>{value}</span>
            <div class="footer-note" style="margin-top:0.2rem;">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_regional_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    return (
        df.copy().style.format(
            {
                "receita": lambda x: format_currency(float(x)),
                "pedidos": lambda x: format_number(float(x)),
                "ticket_medio": lambda x: format_currency(float(x)) if pd.notna(x) else "N/A",
                "frete_medio": lambda x: format_currency(float(x)) if pd.notna(x) else "N/A",
                "prazo_medio": lambda x: f"{x:.1f} dias" if pd.notna(x) else "N/A",
                "atraso_pct": lambda x: format_pct(float(x)) if pd.notna(x) else "N/A",
                "review_medio": lambda x: f"{x:.2f}" if pd.notna(x) else "N/A",
            }
        )
        .background_gradient(subset=["receita"], cmap="Blues")
        .background_gradient(subset=["atraso_pct"], cmap="Reds")
        .background_gradient(subset=["review_medio"], cmap="BuGn")
    )


def render_chart(fig: go.Figure, insight: str) -> None:
    st.plotly_chart(fig, width="stretch")
    st.caption(insight)


def render_temporal_section(df: pd.DataFrame) -> None:
    render_section_header(
        t("Análise Temporal", "Temporal Analysis"),
        t("Tendência, sazonalidade e ritmo operacional", "Trend, seasonality and operational pace"),
        t("Esta seção mostra quando o negócio acelera, onde a sazonalidade aparece e em quais janelas a operação parece mais pressionada.", "This section shows when the business accelerates, where seasonality appears and in which windows operations look more pressured."),
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_chart(chart_revenue_line(df), "A curva de receita destaca aceleração, desaceleração e momentos em que o crescimento merece leitura conjunta com capacidade operacional.")
    with col2:
        render_chart(chart_orders_area(df), "O volume de pedidos ajuda a diferenciar crescimento de receita por demanda versus crescimento por ticket.")
    col3, col4 = st.columns(2, gap="large")
    with col3:
        render_chart(chart_seasonality_heatmap(df), "O heatmap localiza concentração de receita por combinação de mês e dia da semana, sinalizando sazonalidades acionáveis.")
    with col4:
        render_chart(chart_delay_by_period(df), "O atraso por período expõe janelas em que a expansão comercial pode ter tensionado a execução logística.")
    close_section()


def render_category_section(df: pd.DataFrame) -> None:
    render_section_header(
        t("Análise por Categoria", "Category Analysis"),
        t("Quais categorias sustentam resultado, risco e oportunidade", "Which categories sustain results, risk and opportunity"),
        t("A leitura por categoria conecta faturamento, volume, participação e satisfação para separar o que gera escala do que exige correção de rota.", "Category analysis connects revenue, volume, mix and satisfaction to separate what drives scale from what requires course correction."),
    )
    top_row_left, top_row_right = st.columns(2, gap="large")
    with top_row_left:
        render_chart(chart_top_categories_revenue(df), "O ranking por receita revela os grupos com maior peso comercial e maior sensibilidade para preço, estoque e sortimento.")
    with top_row_right:
        render_chart(chart_top_categories_orders(df), "O ranking por pedidos mostra quais categorias sustentam volume transacional e ajudam a separar escala de monetização.")
    render_chart(chart_category_share_donut(df), "A participação por categoria mostra o grau de concentração da receita e a dependência do negócio em poucos clusters.")
    render_chart(chart_category_value_vs_satisfaction(df), "A dispersão cruza preço médio, escala e satisfação para destacar categorias com alto volume e percepção inferior à média.")
    close_section()


def render_geography_section(df: pd.DataFrame, geography_mode: str) -> None:
    geography_label = "cliente" if geography_mode == "Cliente" else "seller"
    render_section_header(
        t("Performance Regional e Gargalos Operacionais", "Regional Performance and Operational Bottlenecks"),
        t(f"Quais UFs geram mais valor e onde o desempenho perde eficiência ({geography_label})", f"Which states generate more value and where performance loses efficiency ({geography_label})"),
        t("A leitura regional mostra quais estados concentram receita, onde o prazo se alonga e onde custo logístico e satisfação entram em tensão.", "Regional analysis shows which states concentrate revenue, where delivery times stretch, and where logistics cost and satisfaction come under tension."),
    )
    regional_df = build_state_table(df).query("pedidos >= 80").copy()
    if regional_df.empty:
        st.info(t("O recorte atual não possui massa suficiente para uma análise regional comparável por UF.", "The current selection does not have enough volume for a comparable state-level analysis."))
        close_section()
        return

    best_revenue = regional_df.sort_values("receita", ascending=False).iloc[0]
    worst_delay = regional_df.sort_values("atraso_pct", ascending=False).iloc[0]

    top_kpi_left, top_kpi_right = st.columns(2, gap="large")
    with top_kpi_left:
        render_regional_kpi(
            "Melhor UF em receita",
            f"{best_revenue['uf']} • {format_currency(float(best_revenue['receita']))}",
            f"{format_number(float(best_revenue['pedidos']))} pedidos e ticket médio de {format_currency(float(best_revenue['ticket_medio']))}.",
        )
    with top_kpi_right:
        render_regional_kpi(
            "Pior UF em taxa de atraso",
            f"{worst_delay['uf']} • {format_pct(float(worst_delay['atraso_pct']))}",
            f"Prazo médio de {worst_delay['prazo_medio']:.1f} dias e review médio de {worst_delay['review_medio']:.2f}.",
        )

    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_chart(chart_state_revenue(df), "O ranking por UF mostra onde a operação concentra maior valor comercial e onde a priorização regional tende a gerar mais retorno.")
    with col2:
        render_chart(chart_state_delivery_time(df), "O prazo médio por UF torna explícito onde o serviço logístico está mais pressionado, mesmo em estados comercialmente relevantes.")

    col3, col4 = st.columns((1.15, 0.85), gap="large")
    with col3:
        table_df = regional_df[["uf", "receita", "pedidos", "ticket_medio", "frete_medio", "prazo_medio", "atraso_pct", "review_medio"]].sort_values("receita", ascending=False)
        st.dataframe(style_regional_table(table_df), width="stretch", height=420)
        st.caption("Tabela analítica por UF com foco em escala comercial, custo logístico e percepção de experiência.")
    with col4:
        render_chart(chart_state_delay_rate(df), "A taxa de atraso por UF ajuda a localizar gargalos operacionais persistentes e orientar revisão de SLA regional.")
        regional_insights_html = "".join(f"<li>{item}</li>" for item in build_regional_insights(df))
        st.markdown(
            f"""
            <div class="regional-kpi" style="margin-top:0.8rem;">
                <strong>Insights regionais</strong>
                <div class="footer-note" style="margin-top:0.35rem;">
                    <ul style="margin:0 0 0 1rem; padding:0; line-height:1.65;">
                        {regional_insights_html}
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    close_section()


def render_operations_section(df: pd.DataFrame) -> None:
    render_section_header(
        t("Operação e Logística", "Operations and Logistics"),
        t("Onde estão os gargalos que afetam SLA, satisfação e eficiência", "Where the bottlenecks affecting SLA, satisfaction and efficiency are"),
        t("A leitura operacional conecta prazo, atraso e percepção do cliente para direcionar ações de SLA, transporte e jornada.", "Operational analysis connects delivery time, delay and customer perception to guide SLA, transport and journey actions."),
    )
    col1, col2 = st.columns(2, gap="large")
    with col1:
        render_chart(chart_delivery_boxplot(df), "A distribuição de prazo mostra dispersão operacional e ajuda a separar rotinas estáveis de exceções severas.")
    with col2:
        render_chart(chart_delay_by_category(df), "Categorias com maior taxa de atraso são candidatas naturais para revisão de SLA, sellers e estratégia de fulfilment.")
    render_chart(chart_delivery_vs_review(df), "O relacionamento entre prazo médio e nota média indica em quais clusters a experiência do cliente é mais sensível à lentidão logística.")
    close_section()


def render_health_section(monitoring_status: dict[str, object] | None) -> None:
    render_section_header(
        t("Saúde da Camada Publicada", "Published-Layer Health"),
        t("Atualização e qualidade da base oficial", "Official data freshness and quality"),
        t("Este bloco resume o estado mais recente do monitoramento recorrente da base usada pelo dashboard.", "This block summarizes the latest recurring monitoring status of the official dataset used by the dashboard."),
    )
    if not monitoring_status:
        st.info(t("O monitoramento recorrente ainda não está disponível neste ambiente. O dashboard segue operacional com a base principal.", "Recurring monitoring is not yet available in this environment. The dashboard remains operational with the main published base."))
        close_section()
        return

    generated_at = str(monitoring_status.get("generated_at_utc") or "N/A")
    total_checks = int(monitoring_status.get("total_checks") or 0)
    failed_checks = int(monitoring_status.get("failed_checks") or 0)
    health_score = monitoring_status.get("health_score") or {}
    score_value = int(health_score.get("score") or 0)
    score_status = str(health_score.get("status") or "unknown")
    main_risk = str(health_score.get("main_risk") or "none")
    status_label = "Saudável" if failed_checks == 0 else "Em alerta"
    if get_format_locale() == "en-US":
        status_label = "Healthy" if failed_checks == 0 else "Attention required"
    results = pd.DataFrame(monitoring_status.get("results") or [])
    history_df = pd.DataFrame(monitoring_status.get("history") or [])
    recommendation = build_health_recommendation(main_risk, failed_checks)

    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        render_regional_kpi(t("Status atual", "Current status"), status_label, t("Última geração UTC:", "Latest UTC generation:") + f" {generated_at}.")
    with col2:
        render_regional_kpi(t("Checks executados", "Executed checks"), format_number(total_checks), t("Cobertura total do monitoramento recorrente.", "Total recurring-monitoring coverage."))
    with col3:
        render_regional_kpi(t("Falhas abertas", "Open failures"), format_number(failed_checks), t("Quantidade de checks em FAIL na última execução.", "Number of FAIL checks in the latest run."))
    with col4:
        render_regional_kpi("Health score", f"{score_value}/100", t("Status:", "Status:") + f" {score_status} | " + t("risco principal:", "main risk:") + f" {main_risk}.")

    st.markdown(
        f"""
        <div class="regional-kpi" style="margin-top:0.85rem;">
            <strong>{t("Ação recomendada", "Recommended action")}</strong>
            <div class="footer-note" style="margin-top:0.35rem;">{recommendation}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not results.empty:
        preview = results[["check_name", "status", "severity", "metric_value"]].copy()
        st.dataframe(preview, width="stretch", height=260)
        st.caption(t("Resumo das verificações mais recentes da base oficial.", "Summary of the latest checks against the official dataset."))
    if not history_df.empty:
        history_df["generated_at_utc"] = pd.to_datetime(history_df["generated_at_utc"], errors="coerce")
        trend = history_df.dropna(subset=["generated_at_utc"]).sort_values("generated_at_utc").tail(12)
        if not trend.empty:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=trend["generated_at_utc"],
                    y=trend["health_score"],
                    mode="lines+markers",
                    name="Health score",
                    line={"color": COLORS["accent"], "width": 3},
                )
            )
            fig.update_layout(
                height=280,
                margin={"l": 24, "r": 24, "t": 24, "b": 24},
                xaxis_title="Execução",
                yaxis_title="Score",
                yaxis_range=[0, 100],
                template="plotly_white",
                showlegend=False,
            )
            st.plotly_chart(fig, width="stretch")
            st.caption(t("Tendência recente do health score da camada publicada.", "Recent trend of the published-layer health score."))
    close_section()


def render_health_summary_compact(monitoring_status: dict[str, object] | None) -> None:
    if not monitoring_status:
        return
    health_score = monitoring_status.get("health_score") or {}
    failed_checks = int(monitoring_status.get("failed_checks") or 0)
    score_value = int(health_score.get("score") or 0)
    main_risk = str(health_score.get("main_risk") or "none")
    recommendation = build_health_recommendation(main_risk, failed_checks)
    st.markdown(
        f"""
        <div class="section-shell" style="padding:0.85rem 1rem;">
            <div class="section-eyebrow">{t("Resumo de Saúde", "Health Summary")}</div>
            <h2 class="section-title">{t("Sinal operacional da camada publicada", "Operational signal from the published layer")}</h2>
            <p class="section-copy">
                {t("Health score atual:", "Current health score:")} <strong>{score_value}/100</strong>.
                {t("Falhas abertas:", "Open failures:")} <strong>{format_number(failed_checks)}</strong>.
                {t("Risco principal:", "Main risk:")} <strong>{main_risk}</strong>.
            </p>
            <p class="footer-note" style="margin-top:0.25rem;">{recommendation}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_semantic_section(semantic_assets: dict[str, pd.DataFrame]) -> None:
    render_section_header(
        t("Camada Semântica", "Semantic Layer"),
        t("Recortes para seller, logística e cohort", "Reusable slices for seller, logistics and cohort analysis"),
        t("Esses recortes ampliam a leitura executiva sem depender da tabela principal em todas as análises.", "These slices expand executive analysis without depending on the main fact table for every readout."),
    )
    if not semantic_assets:
        st.info(t("Os recortes semânticos ainda não estão disponíveis neste ambiente. A navegação principal do dashboard continua disponível.", "Semantic slices are not yet available in this environment. The main dashboard navigation remains available."))
        close_section()
        return

    logistics_df = semantic_assets.get("logistics", pd.DataFrame())
    seller_df = semantic_assets.get("seller", pd.DataFrame())
    cohort_df = semantic_assets.get("cohort", pd.DataFrame())
    executive_kpi_df = semantic_assets.get("executive_kpis", pd.DataFrame())

    top_logistics = logistics_df.sort_values("delayed_rate", ascending=False).head(10) if not logistics_df.empty else pd.DataFrame()
    top_sellers = seller_df.sort_values("delay_rate", ascending=False).head(10) if not seller_df.empty else pd.DataFrame()
    top_cohorts = cohort_df.sort_values(["purchase_cohort_month", "cohort_order_month_number"]).head(12) if not cohort_df.empty else pd.DataFrame()

    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        render_regional_kpi("Slices logísticos", format_number(float(len(logistics_df))), "Recortes agregados por mês e UF origem/destino.")
    with col2:
        render_regional_kpi("Sellers analisáveis", format_number(float(len(seller_df))), "Base comparável por seller pseudonimizado.")
    with col3:
        render_regional_kpi("Linhas de cohort", format_number(float(len(cohort_df))), "Evolução de cohorts por janela de maturação.")
    with col4:
        render_regional_kpi(t("KPIs executivos", "Executive KPIs"), format_number(float(len(executive_kpi_df))), t("Ativo resumido com métricas-chave prontas para reuso.", "Compact asset with key metrics ready for reuse."))

    highlights = []
    if not logistics_df.empty and "delayed_rate" in logistics_df.columns:
        logistics_hotspot = logistics_df.sort_values("delayed_rate", ascending=False).iloc[0]
        highlights.append(
            t(
                f"Logística: maior atraso observado entre {logistics_hotspot.get('seller_state', 'N/A')} e {logistics_hotspot.get('customer_state', 'N/A')}.",
                f"Logistics: highest delay observed between {logistics_hotspot.get('seller_state', 'N/A')} and {logistics_hotspot.get('customer_state', 'N/A')}.",
            )
        )
    if not seller_df.empty and "delay_rate" in seller_df.columns:
        risky_seller = seller_df.sort_values("delay_rate", ascending=False).iloc[0]
        highlights.append(
            t(
                f"Seller: maior risco operacional no tier {risky_seller.get('seller_volume_tier', 'N/A')}.",
                f"Seller: highest operational risk in tier {risky_seller.get('seller_volume_tier', 'N/A')}.",
            )
        )
    if not cohort_df.empty:
        latest_cohort = cohort_df.sort_values(["purchase_cohort_month", "cohort_order_month_number"]).iloc[-1]
        highlights.append(
            t(
                f"Cohort: leitura mais recente em {latest_cohort.get('purchase_cohort_month', 'N/A')} na janela {latest_cohort.get('cohort_order_month_number', 'N/A')}.",
                f"Cohort: latest available readout is {latest_cohort.get('purchase_cohort_month', 'N/A')} at month window {latest_cohort.get('cohort_order_month_number', 'N/A')}.",
            )
        )
    if not executive_kpi_df.empty and {"metric_id", "metric_value"}.issubset(executive_kpi_df.columns):
        metric_count = executive_kpi_df["metric_id"].nunique()
        highlights.append(
            t(
                f"KPIs: {metric_count} definições canônicas já materializadas para reuso entre app, BI e documentação.",
                f"KPIs: {metric_count} canonical definitions already materialized for reuse across app, BI and documentation.",
            )
        )
    if highlights:
        highlights_html = "".join(f"<li>{item}</li>" for item in highlights[:4])
        st.markdown(
            f"""
            <div class="regional-kpi" style="margin-top:0.85rem;">
                <strong>{t("Leitura executiva dos ativos", "Executive readout of semantic assets")}</strong>
                <div class="footer-note" style="margin-top:0.35rem;">
                    <ul style="margin:0 0 0 1rem; padding:0; line-height:1.65;">
                        {highlights_html}
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    tabs = st.tabs([t("Logística", "Logistics"), "Seller", "Cohort", "KPIs"])
    with tabs[0]:
        if top_logistics.empty:
            st.info("Sem dados logísticos materializados.")
        else:
            logistics_view = top_logistics.copy()
            logistics_view["delayed_rate"] = logistics_view["delayed_rate"].mul(100).round(1)
            logistics_view["avg_freight_to_price_ratio"] = logistics_view["avg_freight_to_price_ratio"].mul(100).round(1)
            st.dataframe(logistics_view, width="stretch", height=320)
    with tabs[1]:
        if top_sellers.empty:
            st.info("Sem dados de seller materializados.")
        else:
            seller_view = top_sellers.copy()
            seller_view["delay_rate"] = seller_view["delay_rate"].mul(100).round(1)
            st.dataframe(seller_view, width="stretch", height=320)
    with tabs[2]:
        if top_cohorts.empty:
            st.info("Sem dados de cohort materializados.")
        else:
            st.dataframe(top_cohorts, width="stretch", height=320)
    with tabs[3]:
        if executive_kpi_df.empty:
            st.info("Sem KPIs executivos materializados.")
        else:
            st.dataframe(executive_kpi_df, width="stretch", height=320)
    close_section()


def render_executive_insights(df: pd.DataFrame) -> None:
    render_section_header(
        t("Insights Executivos", "Executive Insights"),
        t("Síntese final para decisão de negócio", "Final synthesis for business decision-making"),
        t("Esta camada final resume o recorte em sinais de ação, destacando o que merece atenção imediata de negócio e operação.", "This final layer summarizes the selected slice into action-oriented signals, highlighting what deserves immediate business and operational attention."),
    )
    cards_html = "".join(f"<div class='insight-card'><h4>{card['title']}</h4><p>{card['text']}</p></div>" for card in build_executive_insights(df))
    st.markdown(f"<div class='insight-grid'>{cards_html}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='footer-note'>{t('Leitura recomendada: primeiro validar tendência e concentração de receita, depois localizar gargalos regionais e, por fim, priorizar ações logísticas com maior impacto em valor e experiência.', 'Recommended reading path: first validate trend and revenue concentration, then locate regional bottlenecks, and finally prioritize logistics actions with the highest impact on value and customer experience.')}</p>",
        unsafe_allow_html=True,
    )
    close_section()


def render_support_tables(df: pd.DataFrame) -> None:
    render_section_header("Apoio Analítico", "Tabelas para exploração detalhada e exportação", "As tabelas abaixo complementam a leitura executiva com recortes prontos para inspeção, documentação e exportação local.")
    category_table = (
        df.groupby("category_label", as_index=False)
        .agg(receita=("total_item_value", "sum"), pedidos=("order_id", "nunique"), preco_medio=("price", "mean"), review_medio=("review_score_mean", "mean"), atraso_pct=("is_delayed", "mean"))
        .sort_values("receita", ascending=False)
        .head(20)
    )
    category_table["atraso_pct"] = category_table["atraso_pct"] * 100
    state_table = build_state_table(df)
    order_table = (
        df[["order_id", "order_status", "selected_state", "category_label", "payment_type_mode", "order_purchase_timestamp", "total_item_value", "delivery_time_days", "estimated_delay_days", "review_score_mean"]]
        .sort_values("order_purchase_timestamp", ascending=False)
        .head(250)
    )
    tabs = st.tabs(["Categorias", "Estados", "Pedidos"])
    for tab, table_name, table_df in [(tabs[0], "categorias", category_table), (tabs[1], "estados", state_table), (tabs[2], "pedidos", order_table)]:
        with tab:
            st.dataframe(table_df, width="stretch", height=380)
            st.download_button(label=f"Exportar tabela de {table_name}", data=to_csv_bytes(table_df), file_name=f"{table_name}_dashboard.csv", mime="text/csv", width="stretch")
    close_section()
