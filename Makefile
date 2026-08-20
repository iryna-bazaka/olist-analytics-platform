RAW_DIR ?= data/raw
DB_PATH ?= data/warehouse/olist.sqlite

.PHONY: pipeline preview test dashboard

pipeline:
	python scripts/run_pipeline.py --raw-dir $(RAW_DIR) --db-path $(DB_PATH)

preview:
	python scripts/generate_dashboard_preview.py --db-path $(DB_PATH)

test:
	python -m unittest discover -s tests -v

dashboard:
	streamlit run app/dashboard.py
