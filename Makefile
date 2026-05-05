install:
	uv sync

lint:
	ruff check src app tests

test:
	pytest --cov=src --cov=app --cov-report=term-missing

pipeline:
	python -c "from src.data_loader import load_dataset; load_dataset()"
	python -c "import pandas as pd; from src.lgpd_classifier import classify_dataframe_columns; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); classify_dataframe_columns(df)"
	python -c "import pandas as pd; from src.lgpd_classifier import classify_dataframe_columns; from src.risk_scoring import calculate_privacy_risk_score; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); classification=classify_dataframe_columns(df); calculate_privacy_risk_score(classification, total_rows=len(df))"
	python -c "import pandas as pd; from src.data_quality import run_data_quality_checks; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); run_data_quality_checks(df)"
	python -c "import pandas as pd; from src.report_generator import generate_markdown_reports; df=pd.read_csv('data/samples/sample_governance_dataset.csv'); generate_markdown_reports(df, docs_dir='docs')"

app:
	streamlit run app/main.py

screenshots:
	python scripts/capture_streamlit_screenshots.py
