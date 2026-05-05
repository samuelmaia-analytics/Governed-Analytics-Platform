install:
	uv sync

lint:
	uv run ruff check src app tests

test:
	uv run pytest --cov=src --cov=app --cov-report=xml

pipeline:
	uv run python -c "from src.data_loader import load_dataset; load_dataset()"
	uv run python -c "import pandas as pd; from src.lgpd_classifier import classify_dataframe_columns; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); classify_dataframe_columns(df)"
	uv run python -c "import pandas as pd; from src.lgpd_classifier import classify_dataframe_columns; from src.risk_scoring import calculate_privacy_risk_score; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); classification=classify_dataframe_columns(df); calculate_privacy_risk_score(classification, total_rows=len(df))"
	uv run python -c "import pandas as pd; from src.data_quality import run_data_quality_checks; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); run_data_quality_checks(df)"
	uv run python -c "import pandas as pd; from src.report_generator import generate_markdown_reports; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); generate_markdown_reports(df, docs_dir='docs')"

app:
	uv run streamlit run app/main.py

screenshots:
	uv run python scripts/capture_streamlit_screenshots.py

clean:
	uv run python -c "from pathlib import Path; import shutil; [shutil.rmtree(p, ignore_errors=True) if Path(p).is_dir() else Path(p).unlink(missing_ok=True) for p in ('.pytest_cache','.ruff_cache','.mypy_cache','coverage.xml')]"
