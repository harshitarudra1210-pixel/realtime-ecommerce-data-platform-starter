# Real-Time E-Commerce Data Platform with Cloud Lakehouse and Data Observability

An end-to-end Data Engineering portfolio project demonstrating an e-commerce data pipeline using Python, SQL, a Bronze-Silver-Gold lakehouse architecture, data quality validation, and pipeline observability.

**Project Status:** Local batch pipeline implemented. Automated tests passing. Streaming, orchestration, and cloud integration are planned future milestones.

## 1. Business Problem

E-commerce platforms generate data from multiple sources, including customers, products, orders, and order events.

Data may contain:
- Missing or invalid values
- Unknown customer references
- Duplicate events
- Invalid timestamps
- Inconsistent records

These issues can affect reporting accuracy and business decisions.

This project demonstrates how to build a repeatable data pipeline that ingests raw data, validates records, separates rejected data, and generates analytics-ready datasets.

## 2. Project Architecture

The pipeline follows a Bronze-Silver-Gold architecture.

**Data Flow:**

Source Data → Ingestion → Bronze → Silver → Gold → Analytics

Invalid records are stored separately in Rejects, while execution information is maintained in Observability.

### Architecture Layers

1. **Source:** Synthetic CSV and JSONL sample data.
2. **Ingestion:** Python loaders read source files and add ingestion metadata.
3. **Bronze:** Preserves ingested source records.
4. **Silver:** Validates and processes records, identifying invalid data.
5. **Rejects:** Stores invalid records with rejection reasons.
6. **Gold:** Produces analytics-ready datasets, including daily order counts.
7. **Observability:** Stores execution summaries, record counts, and pipeline status.

## 3. Current Implementation

| Component | Implementation status |
|---|---|
| Python batch ingestion | Implemented |
| Bronze layer | Implemented |
| Silver validation | Implemented |
| Gold analytics | Implemented |
| Reject handling | Implemented |
| Pipeline run summary | Implemented |
| Automated tests | 6 tests passing |
| GitHub Actions CI | Passing |
| Kafka streaming | Planned |
| Airflow orchestration | Planned |
| Cloud lakehouse | Planned |

## 4. Technology Stack

- **Python:** Data ingestion, validation, and transformation.
- **SQL:** Planned database and analytics operations.
- **CSV / JSONL:** Sample source data formats.
- **Git and GitHub:** Version control and collaboration.
- **pytest:** Automated testing.
- **GitHub Actions:** Continuous integration.

Future technologies:
- PostgreSQL
- Apache Parquet
- Apache Kafka
- Apache Airflow
- Docker
- Cloud data platform

These technologies will be introduced in later milestones.

## 5. Repository Structure

```text
realtime-ecommerce-data-platform-starter/
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── config/
├── data/
│   ├── sample/
│   ├── raw/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   ├── rejects/
│   └── observability/
│
├── docs/
├── sql/
│
├── src/
│   ├── ingestion/
│   ├── validation/
│   ├── main.py
│   ├── pipeline.py
│   └── order_pipeline.py
│
├── tests/
│   ├── test_pipeline.py
│   └── test_starter.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

**Note:** Generated pipeline output folders are maintained locally and excluded from Git tracking. Sample input data and source code are maintained in the repository.

## 6. Prerequisites

- Python 3.11 or above
- Git
- GitHub account
- VS Code (recommended)

## 7. Project Setup

Clone the repository:

```bash
git clone https://github.com/harshitarudra1210-pixel/realtime-ecommerce-data-platform-starter.git
```

Move into the project directory:

```bash
cd realtime-ecommerce-data-platform-starter
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## 8. Running the Pipeline

Run the main pipeline:

```bash
python -m src.main
```

The pipeline processes the available sample data and generates outputs in the local Bronze, Silver, Gold, Rejects, and Observability folders.

## 9. Running Automated Tests

Run all tests:

```bash
python -m pytest -v
```

Current test coverage includes:
- Valid order processing
- Unknown customer rejection
- Invalid and missing timestamps
- Duplicate and missing event IDs
- Pipeline run summary generation
- Starter repository readiness

**Latest verified result:** 6 tests passed.

## 10. GitHub Actions

The repository uses GitHub Actions to execute automated tests when changes are pushed or pull requests are created.

This helps verify that project changes do not break existing functionality.

## 11. Project Milestones

1. Project requirements and architecture design
2. GitHub repository setup and sample data
3. Python ingestion and Bronze layer
4. Silver validation and rejection handling
5. Gold analytics and pipeline observability
6. Automated testing and CI integration
7. Simulated streaming using Kafka
8. Workflow orchestration using Airflow
9. Cloud integration and final project demonstration

## 12. Data Security

- All sample data is synthetic.
- Never commit API keys, passwords, or credentials.
- Keep local `.env` files out of Git.
- Do not use real customer or payment information.

## 13. Project Objective

The objective is to develop practical Data Engineering skills by building a realistic, maintainable, and testable data platform.

The project is developed incrementally, with emphasis on data quality, reliability, testing, observability, and industry-style development practices.
