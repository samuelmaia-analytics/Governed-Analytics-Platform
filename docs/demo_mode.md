# Demo Mode

## Objective

This guide explains how to run the repository in a predictable portfolio/demo mode, focusing on the governed published layer, semantic assets and executive app narrative.

## Recommended Demo Flow

1. Run the end-to-end local pipeline:

```bash
python src/run_platform_pipeline.py
```

2. Confirm the main governed outputs exist:

- `data/published/dashboard/fact_orders_dashboard.parquet`
- `data/published/semantic/executive_kpis_slice.parquet`
- `data/published/monitoring/published_layer_monitoring.json`

3. Launch the Streamlit app:

```bash
streamlit run streamlit_app/app.py
```

4. Use `Português (Brasil)` as the default regional format for the executive walkthrough.

## Suggested Walkthrough Order

1. Header and context
   Explain the publication boundary and the difference between `fact_orders_enriched` and `fact_orders_dashboard`.

2. KPI layer
   Show that the main cards are backed by `executive_kpis_slice`, not only by app-side calculations.

3. Temporal and category sections
   Use them to explain business growth, mix concentration and emerging risks.

4. Geography and operations
   Connect logistics performance, delay risk and customer experience.

5. Health section
   Show freshness, health score, anomaly checks and score history as evidence of operational governance.

6. Semantic section
   Highlight reusable assets for logistics, seller, cohort and executive KPIs.

## Visual Evidence Already Available

- `images/dashboard/01_overview.png`
- `images/dashboard/02_kpis.png`
- `images/dashboard/03_temporal.png`
- `images/dashboard/04_categories.png`
- `images/dashboard/05_geography.png`
- `images/genai/01_product_text_features_openai.png`
- `images/dadosfera/03_colecao_publicada.png`
- `images/dadosfera/04_volume_100k.png`

## Recommended Talking Points

- governed publication is an explicit step, not an implicit by-product
- Streamlit, semantic assets, monitoring and Power BI align to the same published boundary
- privacy-by-design controls are applied before executive exposure
- health score and anomaly checks make the published layer observable as a data product
- dbt was introduced as a complementary modeling and documentation layer, not as unnecessary stack replacement

## Demo Stability Notes

- The local demo is reproducible without mandatory secrets.
- Optional OpenAI and Dadosfera integrations are not required for the main walkthrough.
- If the monitoring freshness check is red, explain it as operational signal, not product failure.
- If you need static presentation material, use the screenshots under `images/` instead of recapturing every run.
