# Source code

Implemented local batch pipeline:
- `pipeline.py`: source ingestion, Bronze lineage, Silver validation/deduplication, rejects, Gold daily order counts, run summary.
- `main.py`: executable entry point.

Run from repository root with `python -m src.main`.
Run tests with `python -m unittest discover -s tests`.
