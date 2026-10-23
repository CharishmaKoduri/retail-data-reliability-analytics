# Retail Data Reliability & Analytics Platform

A Python and PostgreSQL data engineering project focused on retail transaction data quality, controlled ingestion, dimensional modeling, and analytical validation.

## Overview

This project builds a data pipeline around the UCI Online Retail dataset. It investigates data-quality issues, prepares a reviewable dataset, loads transactions into PostgreSQL, builds a dimensional warehouse, and validates the consistency of the resulting analytical data.

The goal is to make data preparation and analytics more transparent, reproducible, and testable.

## Architecture

The current workflow is:

1. **Source inspection** — inspect the original Excel workbook and its schema.
2. **Data-quality auditing** — measure missing values, exact duplicate rows, cancellations, negative quantities, and unusual prices.
3. **Data preparation** — generate cleaned, quarantined, and duplicate-review outputs.
4. **Candidate deduplication** — create a deduplicated candidate dataset while preserving duplicate records for review.
5. **PostgreSQL ingestion** — load the candidate dataset into a raw transaction table and record load metadata.
6. **Analytics layer** — create a transaction analytics view and SQL queries for quality checks and monthly analysis.
7. **Dimensional warehouse** — build product, customer, and date dimensions plus a retail transaction fact table.
8. **Validation** — run SQL integrity checks and automated Python tests to reconcile raw and warehouse data.

## Technology Stack

- **Language:** Python
- **Data processing:** pandas
- **Database:** PostgreSQL
- **Database driver:** Psycopg
- **Testing:** pytest
- **Analytics:** SQL
- **Data formats:** Excel and CSV

## Dataset

The project uses the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online-retail), which contains retail transaction records.

| Dataset metric | Result |
|---|---:|
| Original rows | 541,909 |
| Candidate rows loaded into PostgreSQL | 536,641 |
| Duplicate rows retained for review | 5,268 |
| Rows quarantined during cleaning | 2 |

Duplicate records are treated as candidates for investigation rather than automatically assumed to be errors. Repeated invoice and product lines can be legitimate, so the project retains a review trail.

## Data Quality and Reliability

The pipeline examines several data-quality dimensions:

- Missing customer identifiers
- Exact duplicate records
- Cancellation invoices
- Negative quantities
- Zero and negative unit prices
- Source-to-warehouse reconciliation

The ingestion process records a SHA-256 fingerprint of the input file and uses load metadata to prevent an unchanged file from being loaded again accidentally. Database transactions and an advisory lock help protect the load process from partial or concurrent executions by cooperating loader instances.

## Dimensional Warehouse

The PostgreSQL warehouse uses a star-schema-style structure:

- **`dim_product`** — product identifiers and descriptions
- **`dim_customer`** — customer identifiers and country, including an unknown-customer member
- **`dim_date`** — calendar attributes for transaction dates
- **`fact_retail_transactions`** — transaction-level quantities, prices, line values, and classifications

The fact table is reconciled against the raw transaction table using source row identifiers and transaction-value checks.

## Validation

The project includes automated tests covering:

- Expected raw and fact-table row counts
- Source-row uniqueness
- Analytics-view consistency
- Preservation of missing customer identifiers
- Load fingerprint metadata
- Referential integrity across warehouse dimensions
- Mapping missing customers to the unknown dimension member
- Raw-to-fact row reconciliation
- Transaction-value consistency
- Monthly aggregation reconciliation

**Current validation result:** 12 automated tests passed in the local PostgreSQL environment.

## Repository Structure

```text
retail-data-reliability-analytics/
├── src/       # Python ingestion, cleaning, auditing, and validation scripts
├── sql/       # Table definitions, warehouse loading, checks, and analytics
├── tests/     # Automated database and pipeline tests
├── README.md
├── requirements.txt
├── data_quality_report.csv
└── .gitignore
```

Local input and processed datasets, virtual environments, and database credentials are excluded from version control.

## Running the Tests

After installing the dependencies, configuring the local PostgreSQL connection, and preparing the database schema and data:

```bash
python -m pytest tests/test_pipeline.py -v
```

The current tests use the populated local database and the dataset-specific row counts documented above.

## Limitations and Future Improvements

- Add a fresh-environment setup process to make the pipeline easier to reproduce.
- Expand tests to cover additional malformed inputs and failure scenarios.
- Add incremental ingestion and more comprehensive recovery handling.
- Add cloud storage, orchestration, monitoring, and deployment after the local pipeline is fully documented and repeatable.

## Data Source and Acknowledgment

Dataset: [Online Retail — UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online-retail)

This is a portfolio project for demonstrating data preparation, SQL-based analytics, PostgreSQL warehousing, and data-quality validation.
