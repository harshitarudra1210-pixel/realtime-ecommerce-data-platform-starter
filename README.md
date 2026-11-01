# Real-Time E-Commerce Data Platform with Cloud Lakehouse and Data Observability

A portfolio project that demonstrates an end-to-end data engineering workflow for e-commerce data: ingestion, Bronze/Silver/Gold lakehouse layers, data quality, orchestration, and pipeline observability.

> **Status:** Starter repository / design phase. Features listed here are planned until implemented and tested.

## Business problem
E-commerce data arrives from different sources (customers, products, orders, payments, inventory, and order events). Duplicate events, invalid records, missing data, and inconsistent statuses can make reports unreliable. This project will create a repeatable pipeline that preserves raw inputs, validates and transforms records, and produces analytics-ready datasets.

## Planned architecture
1. **Sources:** CSV/JSON sample files and simulated order events.
2. **Ingestion:** Python loaders record source and ingestion metadata.
3. **Bronze:** Preserve raw input with minimal changes.
4. **Silver:** Validate schema, normalize types, deduplicate by documented rules, and quarantine invalid records.
5. **Gold:** Publish business-ready metrics such as daily sales and product performance.
6. **Observability:** Record run status, counts, errors, and data-quality results.
7. **Orchestration:** Add workflow scheduling after the local batch pipeline is working.

## Repository structure
```text
.github/workflows/    CI workflow
config/               Configuration examples
data/sample/          Small synthetic sample inputs
data/bronze/          Local raw-layer output (generated)
data/silver/          Local cleaned output (generated)
data/gold/            Local analytics output (generated)
docs/                 Product specification and high-level design
sql/                  Schema and analytics SQL
src/                  Python application code
tests/                Automated tests
```

## Proposed technology stack
- Python and SQL for ingestion and transformations
- PostgreSQL for relational storage (planned)
- Parquet for analytics files (planned)
- Kafka for simulated event streaming (later milestone)
- Airflow for orchestration (later milestone)
- pytest for automated tests
- Docker and a cloud platform only after the local version works and the stack is approved

Do not install every tool at once. Start with Python, Git/GitHub, and a small local batch pipeline.

## Quick start
1. Install Python 3.11+ and Git.
2. Clone this repository or download the ZIP.
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
4. Activate it:
   - Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
5. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run tests:
   ```bash
   pytest
   ```

The starter tests are intentionally minimal. Pipeline functionality will be added milestone by milestone.

## Milestones
1. Product specification and architecture review
2. Repository and synthetic sample data
3. Batch ingestion and Bronze layer
4. Silver validation and Gold analytics
5. Data quality results and idempotent reruns
6. Simulated streaming and orchestration
7. Monitoring, tests, documentation, and demo

## Data and security
All included sample data is synthetic. Never commit credentials, API keys, private customer data, or real payment details. Use `.env` locally and keep it out of Git.
