# Target Architecture and Roadmap

## Objective

This document translates the current repository state into a practical target architecture and an implementation roadmap to elevate the project from a strong analytics engineering case into a more explicit governed analytics product.

The recommendations preserve the existing backbone:

- Python remains the operational backbone
- the `curated` versus `published` separation remains the architectural core
- DuckDB remains the local analytical engine
- Streamlit remains the primary executive app
- Power BI remains a complementary consumption channel
- governance, privacy, cataloging, documentation and CI remain first-class concerns

## Current-State Diagnosis

### What is already strong

- The project has a clear and defensible separation between internal analytical modeling and published consumption.
- Publication is a formal pipeline step, not an informal convention.
- Privacy-by-design is materialized through minimization, pseudonymization and contract validation.
- The repository already behaves more like a product than a notebook portfolio:
  - tests
  - CI
  - governance contracts
  - runbooks
  - monitoring artifacts
  - catalog artifacts
  - executive-facing outputs
- The Streamlit app consumes the published layer instead of the internal analytical layer.
- Semantic published assets already exist and support executive and operational storytelling.
- Documentation quality is well above average for portfolio projects.

### Main gaps

- Metric definitions are still spread across Python transformations, Streamlit logic, SQL and BI exports.
- The semantic layer is useful, but it is not yet a canonical metric layer with reusable business definitions.
- Power BI exports are still derived from the internal analytical layer, which weakens the single-source-of-truth story.
- The app still contains business logic that should increasingly live in shared semantic assets.
- GenAI exists today as a bonus capability, but not yet as a governed analytical capability directly connected to the published layer and executive workflows.
- Observability is solid but still mostly check-based; it can evolve into a clearer product health model.

### Architectural risks

- Semantic drift between Streamlit, Power BI and SQL if business logic continues to live in multiple places.
- Published assets may look mature, but consumption inconsistency weakens executive trust if different channels rely on different upstream semantics.
- Custom Python transformations are fine today, but long-term maintainability and explainability improve if tabular transformations become more model-driven.
- GenAI can become cosmetic if it is not explicitly constrained to deterministic context and auditable outputs.

### What is missing to look like an executive analytics product

- A canonical business metric catalog
- A business glossary with standardized definitions
- A stronger semantic layer with reusable marts and metrics
- dbt-powered documentation, tests and lineage
- A single consumption contract across Streamlit and Power BI
- A published-layer health score
- A more explicit product brief and executive scorecard narrative
- Auditable GenAI patterns tied to published data and monitored outputs

## Target Architecture

## Summary

The target state keeps Python as the orchestration and operational layer, while introducing dbt as a complementary transformation, testing and documentation layer.

High-level design:

1. Python performs ingestion, inventory, local orchestration, privacy controls, publication gates, monitoring, cataloging and application delivery.
2. dbt performs staged SQL modeling, semantic marts, tests, docs and lineage over DuckDB.
3. The published layer becomes the official exposure boundary for all downstream consumption.
4. Streamlit, Power BI and GenAI consume the same governed published assets.

## Target flow

```text
raw landing
  -> standardized
  -> dbt staging
  -> dbt intermediate
  -> dbt core marts
  -> governed published marts
  -> semantic marts / executive scorecards
  -> Streamlit / Power BI / GenAI / monitoring
```

## Recommended repository extension

```text
docs/
  target_architecture_and_roadmap.md
  product_brief.md
  metric_catalog.md
  business_glossary.md
  executive_scorecard.md
  incident_runbook.md
  demo_mode.md

dbt/
  dbt_project.yml
  profiles.yml.example
  models/
    sources/
    staging/
    intermediate/
    marts/
    exposures/
  macros/
  seeds/

data/
  curated/
    genai/
      prompts/
      logs/
      outputs/
```

## Prioritized Roadmap

### Quick wins

- Make Power BI consume the published layer or published semantic marts rather than the internal analytical layer.
- Create a canonical metric catalog with formulas, grain, owners and allowed consumption channels.
- Create a business glossary aligned with Streamlit, Power BI and SQL outputs.
- Add a published-layer health score derived from freshness, schema, volume, nulls, semantic coverage and anomaly status.
- Strengthen README positioning from "pipeline + dashboard" to "governed analytics product".
- Add a one-page product brief for executive and recruiter audiences.

### Intermediate improvements

- Introduce `dbt-duckdb` for semantic and published marts first.
- Add dbt tests for keys, nullability, accepted values and relationships.
- Generate dbt docs and include screenshots/evidence in the repository narrative.
- Reduce semantic logic in the Streamlit application by moving recurring calculations upstream.
- Add anomaly detection for executive KPIs such as revenue, delay rate, ticket and order volume.
- Create an incident runbook for published-layer failures and data-quality regressions.

### Advanced evolution

- Migrate the core analytical fact model into dbt after semantic/published adoption stabilizes.
- Add snapshots or controlled historical versioning for selected dimensions or benchmark outputs.
- Add scorecards by seller, state and category.
- Add a forecast / what-if layer for executive planning scenarios.
- Add auditable GenAI copilots tied to published metrics and monitoring outputs.
- Add a reproducible demo mode with a small curated sample and pre-generated artifacts.

## dbt Adoption Proposal

## Why dbt belongs here

dbt should not replace the whole Python pipeline. It should complement the parts of the project where model transparency, SQL modularity, tests, lineage and documentation matter most.

Best fit in this repository:

- tabular transformations
- semantic marts
- published marts
- schema and relationship tests
- documentation generation
- exposures and lineage

Python should remain responsible for:

- ingestion and file validation
- orchestration
- publication gates and privacy controls
- monitoring outputs
- catalog sync and platform integration
- Streamlit app delivery
- GenAI integrations and audit logging

## Recommended dbt structure

```text
dbt/
  dbt_project.yml
  profiles.yml.example
  models/
    sources/
      olist_sources.yml
    staging/olist/
      stg_olist__orders.sql
      stg_olist__order_items.sql
      stg_olist__customers.sql
      stg_olist__products.sql
      stg_olist__sellers.sql
      stg_olist__payments.sql
      stg_olist__reviews.sql
      stg_olist__translation.sql
      _staging.yml
    intermediate/commerce/
      int_orders__payments_agg.sql
      int_orders__reviews_agg.sql
      int_orders__base_join.sql
      int_orders__customer_features.sql
      int_orders__seller_features.sql
      _intermediate.yml
    marts/core/
      fct_orders_enriched.sql
      _core.yml
    marts/published/
      fct_orders_dashboard.sql
      mart_logistics_slice.sql
      mart_seller_scorecard.sql
      mart_customer_cohort.sql
      mart_category_performance.sql
      mart_state_performance.sql
      mart_executive_kpis.sql
      _published.yml
    exposures/
      exposures.yml
  macros/
    pseudonymize.sql
  seeds/
    metric_catalog.csv
```

## Where dbt enters the current flow

Recommended sequence:

1. `inventory`
2. `profiling`
3. Python standardization
4. dbt `staging` and `intermediate`
5. dbt `core` marts
6. Python privacy gate or dbt-published build plus Python validation
7. dbt semantic marts
8. monitoring, catalog, exports and app consumption

Initial implementation without breakage:

- Phase 1: use dbt only for semantic marts and published marts
- Phase 2: migrate `fact_orders_enriched` into dbt
- Phase 3: simplify redundant Python transformations

## Staging / intermediate / marts guidance

### Staging

Role:

- normalize names
- cast types
- preserve source-level traceability
- avoid business-heavy logic

### Intermediate

Role:

- aggregate payments and reviews
- prepare reusable joins
- derive reusable business building blocks

### Marts

Role:

- `core`: analytical fact models
- `published`: governed consumption-facing marts
- `semantic`: executive and operational read models

## dbt tests to implement

Schema tests:

- `not_null`
- `unique`
- `accepted_values`
- `relationships`

Recommended examples:

```yaml
models:
  - name: fct_orders_enriched
    columns:
      - name: order_item_pk
        tests:
          - not_null
          - unique
      - name: order_status
        tests:
          - accepted_values:
              values: ['created', 'approved', 'invoiced', 'processing', 'shipped', 'delivered', 'canceled', 'unavailable']
      - name: seller_id
        tests:
          - relationships:
              to: ref('stg_olist__sellers')
              field: seller_id
```

Custom tests worth adding:

- `price >= 0`
- `freight_value >= 0`
- `delivery_time_days >= 0 when present`
- no forbidden columns in the published exposure table
- no unexpected nulls in published KPI support columns

## dbt docs and exposures

Use `dbt docs generate` to provide:

- model descriptions
- column descriptions
- lineage
- owners
- tags by domain

Recommended exposures:

```yaml
exposures:
  - name: streamlit_executive_dashboard
    type: dashboard
    owner:
      name: Samuel Maia
    depends_on:
      - ref('fct_orders_dashboard')
      - ref('mart_executive_kpis')
      - ref('mart_state_performance')

  - name: power_bi_executive_dashboard
    type: dashboard
    owner:
      name: Samuel Maia
    depends_on:
      - ref('mart_executive_kpis')
      - ref('mart_category_performance')
      - ref('mart_state_performance')
```

## DuckDB local integration

Recommended profile concept:

- DuckDB database file inside `data/`
- sources pointing to Parquet files in `data/standardized/`
- materializations as tables or views depending on portability needs

Suggested local target:

```text
data/platform.duckdb
```

This keeps the project simple, reproducible and aligned with the current stack.

## How dbt coexists with the Python pipeline

The right operating model is hybrid:

- Python orchestrates
- dbt models
- Python validates exposure and runs product operations

This avoids rework and preserves what is already good.

## GenAI Proposal With Real Utility

## Business-relevant use cases

### KPI summary generation

Use deterministic KPI computations and let the LLM produce concise executive narrative such as:

- what changed
- where the largest variance happened
- which dimension drove the change
- what action should be considered

### Deviation explanation

Build deterministic drivers first:

- top states by revenue delta
- top categories by delay delta
- top sellers by SLA degradation

Then let the LLM explain those drivers in business language.

### Insight generation by slice

Supported analytical slices:

- period
- category
- state
- seller
- product family

### Q&A over published metrics

Allow questions only over:

- published metrics
- business glossary
- metric catalog
- monitoring outputs

Do not let the LLM invent SQL or answer from the internal layer by default.

### Alert interpretation

When monitoring fails, generate:

- plain-language incident summary
- likely business impact
- recommended first action
- escalation severity

## Governance, cost and security rules

- Only use published or approved semantic assets as GenAI context.
- Keep all metric calculations deterministic.
- Keep LLM temperature low.
- Version prompts and templates.
- Log prompt version, model, source assets, filters and output hashes.
- Cache by context hash to control cost.
- Use fallback deterministic summaries when the LLM is unavailable.
- Never use GenAI to bypass governance contracts.

## Deterministic vs LLM-assisted split

### Deterministic

- KPI calculation
- period-over-period delta
- anomaly flagging
- contract evaluation
- severity assignment
- dataset filtering
- metric lookup
- retrieval of approved context

### LLM-assisted

- executive narrative
- concise explanation of monitored incidents
- natural-language Q&A over approved business semantics
- guided interpretation of published outputs

## Suggested GenAI architecture

```text
published marts + metric catalog + monitoring outputs
  -> context builder
  -> prompt template registry
  -> LLM
  -> structured response
  -> audit log
  -> Streamlit presentation
```

## Prompt and output audit trail

Recommended structure:

```text
data/curated/genai/
  prompts/
    prompt_registry.yml
  logs/
    genai_requests.jsonl
    genai_responses.jsonl
    genai_audit.csv
  outputs/
    executive_kpi_summaries/
    alert_interpretations/
```

Suggested audit fields:

- `run_id`
- `prompt_id`
- `prompt_version`
- `model_name`
- `temperature`
- `source_asset`
- `source_snapshot`
- `context_hash`
- `filters_applied`
- `latency_ms`
- `token_usage`
- `response_hash`
- `review_status`

## Semantic Layer Improvements

## Core business metrics to formalize

Recommended canonical metrics:

- `revenue_gross`
- `orders`
- `customers`
- `avg_ticket`
- `avg_freight_per_item`
- `delay_rate`
- `on_time_rate`
- `avg_delivery_time_days`
- `repurchase_rate`
- `retention_m1`
- `retention_m3`
- `seller_order_count`
- `seller_otd_rate`
- `seller_avg_delivery_days`
- `customer_lifetime_value_proxy`

## Naming standard

- Technical metric ids in English and snake_case
- Executive display labels in Portuguese
- Explicit formula per metric
- Explicit allowed grain
- Explicit owner and source model

## Reusable metric layer

Recommended file:

```text
docs/metric_catalog.md
```

And optionally a structured source:

```text
dbt/seeds/metric_catalog.csv
```

Suggested fields:

- `metric_id`
- `display_name_pt`
- `definition`
- `formula_sql`
- `grain`
- `owner`
- `source_model`
- `published`
- `used_in_streamlit`
- `used_in_power_bi`

## Reducing ambiguity between Streamlit, Power BI and SQL

Target rule:

- metrics are defined once
- semantic marts are reused by every consumer
- app code formats and displays metrics, but does not become the primary place where metric logic is born

This is one of the highest-impact maturity upgrades in the whole project.

## Business glossary proposal

Recommended document sections:

- business term
- operational meaning
- analytical definition
- exclusions
- owner
- consumption notes

Terms to prioritize:

- revenue
- order
- customer
- active seller
- delayed order
- cohort
- retention
- ticket
- SLA
- seller performance

## Observability and Reliability Improvements

## Stronger data quality checks

Add checks for:

- unexpected distribution shifts
- sudden KPI variance by period
- out-of-range ratio metrics
- semantic mart row-count stability
- contract drift between published assets and consumers

## Freshness checks

Current freshness is file-based. Evolve to:

- freshness by critical asset
- freshness by semantic mart
- freshness by scheduled run expectation

## Anomaly detection

Start simple and deterministic:

- moving average and rolling z-score
- revenue anomaly
- order volume anomaly
- delay-rate anomaly
- avg ticket anomaly

This is enough for a portfolio project and feels realistic.

## Pipeline SLA monitoring

Add:

- expected runtime by step
- step delay thresholds
- stale publication threshold
- last successful run timestamp

## Simplified lineage

Short term:

- document lineage in markdown

Medium term:

- surface dbt lineage artifacts

## Incident runbook

Recommended sections:

- symptom
- likely causes
- immediate containment
- validation queries
- rollback or republish steps
- stakeholder communication note

## Published-layer health score

Suggested weighted model:

- freshness: 25
- schema integrity: 20
- row volume: 15
- critical nulls: 15
- relationship integrity: 10
- anomaly status: 10
- semantic coverage: 5

Output example:

```text
published_health_score: 93
status: healthy
main_risk: none
```

## Actionable alerts

Each alert should contain:

- what failed
- observed value
- expected threshold
- impacted asset
- likely business impact
- first recommended action

## Executive Positioning Improvements

## How to make the project more convincing to executives and recruiters

- Lead with product value, not only technical components.
- Emphasize the published layer as an exposure contract.
- Show that governance was built into the product, not added later.
- Show consumption consistency across Streamlit and Power BI.
- Add scorecards and health indicators to reinforce product ownership.

## Executive documents to add

- `docs/product_brief.md`
- `docs/metric_catalog.md`
- `docs/business_glossary.md`
- `docs/executive_scorecard.md`
- `docs/incident_runbook.md`
- `docs/demo_mode.md`
- `docs/architecture_one_pager.md`

## README rewrite guidance

README should more explicitly highlight:

- governed analytics product thesis
- published consumption contract
- privacy-by-design controls
- reusable semantic assets
- operational health and monitoring
- multi-channel executive consumption

## Evidence to include

- architecture diagram
- published-layer lineage snapshot
- dbt docs screenshot
- executive dashboard screenshots
- monitoring/health-score screenshot
- GenAI audited output screenshot
- scorecard screenshot

## Extra Differentiators

### More mature data contracts

Add contract fields for:

- owner
- SLA
- classification
- expected grain
- freshness expectation
- downstream consumers

### Analytical serving layer

Do not add a new platform. Keep it simple:

- use published marts as a lightweight serving layer
- make them the default contract for executive consumption

### Benchmark / forecast / what-if

High-value, low-hype additions:

- monthly forecast baseline
- best/worst seller scenarios
- freight pressure what-if
- category growth benchmark

### Executive scorecards

Useful assets:

- seller scorecard
- state scorecard
- category scorecard
- published product health scorecard

### Cost awareness

Make cost discipline explicit for GenAI:

- cache strategy
- low-temperature default
- approved models only
- token logging

### Privacy by design

Already strong. Make it more explicit by adding:

- purpose limitation statements per asset
- allowed consumer list
- approved publication rationale

### Stronger CI/CD

Add future steps:

- dbt build
- dbt test
- docs generation validation
- semantic contract checks

### Snapshots / data versioning

Add selectively:

- monthly KPI snapshots
- semantic mart snapshots
- monitor summary history

### Reproducible demo mode

Add:

- small sample dataset
- pre-generated published artifacts
- one-command demo build

## Backlog

### P1

- route Power BI to published assets
- create metric catalog
- create business glossary
- add published health score
- update README positioning
- add product brief

### P2

- add dbt project with DuckDB
- migrate semantic marts into dbt
- add dbt tests
- generate dbt docs
- create incident runbook

### P3

- move core fact model into dbt
- add anomaly detection
- add GenAI KPI summary and alert interpretation
- add audit logging for GenAI

### P4

- add scorecards
- add snapshot/versioning strategy
- add benchmark/forecast/what-if
- add demo mode

## Implementation Plan by Phase

### Phase 1: Semantic consolidation

- standardize metrics
- align consumers
- reduce semantic drift

### Phase 2: dbt introduction

- model semantic and published assets in dbt
- add tests and docs
- preserve Python orchestration

### Phase 3: Reliability and GenAI

- expand monitoring
- add health scoring
- add audited GenAI executive assistants

### Phase 4: Executive differentiation

- scorecards
- benchmarks
- forecast
- demo packaging

## Repository Change Checklist

- add `dbt/`
- add `docs/product_brief.md`
- add `docs/metric_catalog.md`
- add `docs/business_glossary.md`
- add `docs/executive_scorecard.md`
- add `docs/incident_runbook.md`
- add `docs/demo_mode.md`
- update Power BI exports to use published semantics
- reduce metric logic in Streamlit app layer
- add GenAI prompt and log folders
- update CI workflows to include dbt when introduced

## Final Executive Narrative

Recommended thesis for README and LinkedIn:

"This project demonstrates how to turn raw transactional data into a governed analytics product with a formal publication boundary, privacy-by-design controls, reusable semantic assets, executive consumption channels, operational monitoring and a pragmatic roadmap toward dbt-enabled modeling and auditable GenAI."

That narrative is credible because it matches the repository reality and the next maturity steps without overselling unsupported enterprise capabilities.
