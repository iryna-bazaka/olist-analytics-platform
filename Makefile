RAW_DIR ?= data/raw

.PHONY: build test-fixtures fixtures

build:
	dbt build

fixtures:
	python scripts/make_fixtures.py

test-fixtures:
	dbt build --vars '{raw_dir: tests/fixtures}'
