# Local Data Lake Layers

This project uses a local filesystem Data Lake to simulate production-style
promotion controls without claiming that an enterprise cloud platform is running
behind the portfolio demo.

The canonical layer contract is versioned in
`config/data_lake_layers.yml`. Python code can inspect it through
`src.data_lake_layers`.

## Layer Mapping

| Data Lake layer | Local paths | Governance intent |
| --- | --- | --- |
| Bronze | `data/raw/landing/`, `data/external/` | Preserve source-aligned files and externally supplied samples. |
| Silver | `data/standardized/`, `data/staging/` | Hold standardized, profiled, validation-ready analytical inputs. |
| Gold | `data/curated/`, `data/published/` | Hold governed marts, semantic slices, publication evidence, and Streamlit-safe outputs. |
| Quarantine | `data/quarantine/` | Isolate rejected records, failed validation extracts, and unsafe publication candidates. |

## Promotion Rules

Data movement is intentionally gated:

1. Bronze to Silver requires ingestion or standardization code.
2. Silver to Gold requires quality, schema, and LGPD evidence.
3. Gold to Published requires a publication gate decision.
4. Quarantine data must not be consumed by Streamlit or publication outputs.

## Portfolio Boundary

The layout is production-inspired and operationally realistic, but local. It is
designed to demonstrate data governance mechanics, not to represent a live
enterprise Data Lake service.
