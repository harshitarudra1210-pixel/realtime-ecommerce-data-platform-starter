# High-Level Design (HLD)

## 1. Purpose
Build a portfolio-grade e-commerce data platform that ingests synthetic batch data and simulated order events, preserves raw inputs, creates validated datasets, and produces business-ready metrics with observable pipeline runs.

## 2. Logical components
- **Source data:** CSV/JSON files generated for customers, products, orders, payments, inventory, and order events.
- **Ingestion service:** Reads source files and records source name, ingestion timestamp, and run ID.
- **Bronze layer:** Immutable or append-oriented raw landing area.
- **Silver layer:** Schema validation, normalization, referential checks, duplicate handling, and rejected-record capture.
- **Gold layer:** Aggregated datasets for daily sales, order status, and top products.
- **Quality and observability:** Rule-level pass/fail records, processed/rejected counts, duration, and error details.
- **Orchestration:** A later milestone will schedule dependent tasks with retries.
- **Consumers:** SQL queries, reports, and optional dashboard.

## 3. Data flow
```text
CSV / JSON / Simulated Events
            |
            v
      Ingestion (Python)
            |
            v
       Bronze (raw)
            |
            v
  Silver (clean + validated) ---> Rejected records
            |
            v
       Gold (aggregates)
            |
            v
       Reports / Dashboard

Across all stages: run logs + quality results + metrics
```

## 4. Initial data entities
- `customers(customer_id, region, created_at)`
- `products(product_id, category, unit_price)`
- `orders(order_id, customer_id, order_ts, order_status)`
- `order_items(order_id, product_id, quantity, unit_price)`
- `payments(payment_id, order_id, amount, payment_status)`
- `inventory(product_id, available_stock, updated_at)`
- `order_events(event_id, order_id, event_type, event_ts)`
- `pipeline_runs(run_id, started_at, finished_at, status, input_count, output_count, rejected_count, error_message)`
- `quality_results(run_id, rule_id, status, failed_count, details)`

Final columns, types, keys, and deduplication policy should be confirmed during implementation.

## 5. Reliability and quality design
- Preserve original input in Bronze for traceability.
- Define deterministic validation and deduplication rules.
- Route invalid records to a reject/quarantine output with reasons.
- Make reruns idempotent where practical.
- Record pipeline run IDs and source metadata.
- Test key business totals by reconciling Gold metrics to valid Silver records.

## 6. Security and cost
- Use synthetic data only.
- Keep credentials in local environment variables; never commit `.env`.
- Begin locally; use cloud resources only after approval and cost review.

## 7. Delivery phases
1. Specification and repository setup
2. Sample data and batch ingestion
3. Silver transformations and data-quality checks
4. Gold analytics SQL
5. Observability and tests
6. Simulated events and orchestration
7. Optional cloud deployment and dashboard
