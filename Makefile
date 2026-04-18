.PHONY: help install build test lint run-dashboard airflow-up airflow-down deploy docs clean

help:
	@echo "FleetPulse — available targets:"
	@echo "  install        Install Python runtime + dev dependencies"
	@echo "  build          Run dbt build (compile + run + test)"
	@echo "  test           Run dbt test + pytest"
	@echo "  lint           Run sqlfluff + ruff"
	@echo "  run-dashboard  Launch the Streamlit dashboard locally"
	@echo "  airflow-up     Start Airflow stack (Docker Compose)"
	@echo "  airflow-down   Stop Airflow stack"
	@echo "  docs           Generate and serve dbt docs"
	@echo "  deploy         Deploy dbt models to production target"
	@echo "  clean          Remove build artifacts"

install:
	pip install -r requirements.txt -r requirements-dev.txt
	cd dbt && dbt deps

build:
	cd dbt && dbt build

test:
	cd dbt && dbt test
	pytest tests/

lint:
	sqlfluff lint dbt/models
	ruff check .

run-dashboard:
	streamlit run streamlit/app.py

airflow-up:
	docker compose up -d

airflow-down:
	docker compose down

docs:
	cd dbt && dbt docs generate && dbt docs serve

deploy:
	cd dbt && dbt build --target prod

clean:
	rm -rf dbt/target dbt/dbt_packages dbt/logs
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
