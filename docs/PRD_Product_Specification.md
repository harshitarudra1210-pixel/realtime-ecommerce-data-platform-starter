# Product Requirements Document (PRD)
## Real-Time E-Commerce Data Platform with Cloud Lakehouse and Data Observability

**Document status:** Draft for senior review  
**Project type:** Learning and portfolio project  
**Data policy:** Synthetic/public data only

## 1. Project overview and problem statement
E-commerce data arrives from multiple sources, including customers, products, orders, payments, inventory, and order events. Duplicate events, missing records, invalid values, and inconsistent order/payment statuses can lead to unreliable reporting. The platform will collect, preserve, validate, transform, and publish data for trustworthy analytics.

## 2. Goals and success criteria
- Ingest CSV/JSON data and simulated events.
- Preserve raw data in Bronze.
- Validate and clean data in Silver.
- Produce analytics-ready Gold datasets.
- Record data-quality outcomes and pipeline run status.
- Provide repeatable setup and test instructions.

Proposed acceptance examples: duplicate event IDs are handled by a documented rule; invalid records have rejection reasons; Gold totals reconcile to the corresponding valid Silver records; a failed run is visible in logs.

## 3. Scope and non-goals
**In scope:** batch ingestion, simulated streaming, Bronze/Silver/Gold layers, data-quality rules, orchestration, pipeline logs, analytics SQL, automated tests, documentation.

**Initial non-goals:** a customer-facing shopping website, real payment processing, real card data, production-scale infrastructure, machine-learning recommendations, or paid cloud resources without approval.

## 4. Functional requirements
- **FR-01:** Load synthetic CSV/JSON source files.
- **FR-02:** Capture source and ingestion metadata.
- **FR-03:** Store raw inputs in Bronze.
- **FR-04:** Validate and transform data into Silver.
- **FR-05:** Handle duplicate records using explicit keys/rules.
- **FR-06:** Produce Gold analytics datasets.
- **FR-07:** Record pipeline run IDs, timestamps, counts, status, and errors.
- **FR-08:** Persist data-quality results.
- **FR-09:** Preserve invalid records with rejection reasons.
- **FR-10:** Process simulated order events.
- **FR-11:** Orchestrate dependent tasks and supported retries.
- **FR-12:** Provide a monitoring report or optional dashboard.
- **FR-13:** Include automated tests and reproducible run instructions.

## 5. Non-functional requirements
Reliability, maintainability, observability, security, reproducibility, cost control, and measurable performance. Idempotency should be implemented and tested rather than assumed.

## 6. Proposed data model
- `customers`: customer ID, region, creation date
- `products`: product ID, category, unit price
- `orders`: order ID, customer ID, order timestamp, status
- `order_items`: order ID, product ID, quantity, unit price
- `payments`: payment ID, order ID, amount, payment status
- `inventory`: product ID, available stock, update timestamp
- `order_events`: event ID, order ID, event type, event timestamp
- `pipeline_runs`: run ID, start/end time, status, counts, error
- `quality_results`: run ID, rule ID, pass/fail, failure count, details

Exact column types, primary/foreign keys, and event deduplication policy are implementation decisions to review.

## 7. Data flow and lakehouse layers
Sources (CSV/JSON/events) -> ingestion -> Bronze raw data -> Silver validated/cleaned data -> Gold business aggregates -> reports. Quality results and pipeline run logs span all layers.

- **Bronze:** preserve source data and ingestion metadata.
- **Silver:** normalize types, validate required fields and relationships, handle duplicates, quarantine invalid records.
- **Gold:** publish daily sales, order status summaries, and product performance.

## 8. Processing and orchestration
- **Batch:** process a group of files.
- **Streaming:** receive event records continuously; first version may simulate this locally.
- **Orchestration:** execute tasks in dependency order and record retries/status.
Kafka is a potential event transport; Airflow is a potential workflow orchestrator. They serve different purposes and are later milestones, not required for the first local run.

## 9. Data quality and observability
Quality rules may check required IDs, duplicate event IDs, positive quantities, valid statuses, customer/product references, and payment/order consistency. Observability should report run status, counts processed/rejected, duration, last successful run, task failures, and error messages.

## 10. Proposed technology stack
Python, SQL, Git/GitHub, pytest, Parquet, PostgreSQL, and optionally Kafka, Spark, Airflow, Docker, Delta Lake/Iceberg, and Power BI. Begin with a local stack and confirm cloud/platform choices with the senior before adding paid services.

## 11. Acceptance criteria
- A developer can follow the README to set up the project.
- Expected Bronze/Silver/Gold outputs are produced by implemented stages.
- Invalid test records are detected with reasons.
- Reruns do not create unintended duplicates.
- Simulated failures are visible in logs.
- Gold metrics reconcile to validated source records.
- Automated tests pass.

## 12. Risks, assumptions, dependencies
**Risks:** setup complexity, cloud costs, duplicate/late events.  
**Assumptions:** synthetic data, portfolio use, stack subject to senior review.  
**Dependencies:** Python, Git/GitHub, sample data, and approved local tools.

## 13. Deliverables
PRD, HLD, architecture diagram, repository/README, data dictionary, ingestion/transformation code, sample data, tests, quality report, pipeline logs, Gold outputs, setup instructions, and demo.

## 14. Milestones
M1 specification/design review; M2 repository/sample data; M3 batch ingestion/Bronze; M4 Silver/Gold; M5 streaming/orchestration; M6 observability; M7 final testing/demo.

## 15. Questions for senior review
- Which cloud platform, if any, is approved?
- Are Kafka and Airflow required in the first version?
- Should the lakehouse use Delta Lake or Iceberg?
- Is a dashboard required?
- What are the deadline, coding standards, and evaluation criteria?

## 16. Approval
Status: Pending senior review.  
Possible decisions: Approved / Approved with changes / Rework required.
