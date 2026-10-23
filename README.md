\# Retail Data Reliability \& Analytics Platform



\## Overview



A Python and PostgreSQL data engineering project for inspecting, validating, cleaning, reviewing duplicate candidates, loading, and analyzing retail transaction data.



The project uses the UCI Online Retail dataset to demonstrate data-quality analysis, source-row traceability, database loading, dimensional modeling, and automated validation.



\## Architecture



The project follows this workflow:



1\. \*\*Source inspection\*\* — inspect the original Excel workbook and its schema.

2\. \*\*Data-quality auditing\*\* — measure missing values, exact duplicates, cancellations, negative quantities, and unusual prices.

3\. \*\*Data preparation\*\* — generate cleaned, quarantined, and duplicate-review outputs.

4\. \*\*Candidate deduplication\*\* — create a deduplicated candidate dataset while retaining duplicate records for review.

5\. \*\*PostgreSQL ingestion\*\* — load the candidate dataset into a raw transaction table and record load metadata.

6\. \*\*Analytics layer\*\* — create a transaction analytics view and SQL queries for data-quality checks and monthly sales analysis.

7\. \*\*Dimensional warehouse\*\* — create product, customer, and date dimensions plus a retail transaction fact table.

8\. \*\*Validation\*\* — run SQL integrity checks and automated Python tests.



\## Technology



\- Python

\- pandas

\- PostgreSQL

\- Psycopg

\- pytest

\- SQL

\- python-dotenv



\## Dataset



The project uses the UCI Online Retail dataset.



\- \*\*Original rows:\*\* 541,909

\- \*\*Deduplicated candidate rows loaded:\*\* 536,641

\- \*\*Exact duplicate rows retained for review:\*\* 5,268



Exact matching does not prove that repeated transactions are erroneous. The deduplicated dataset is treated as a candidate view, and duplicate records are retained in a separate review output.



\## Data-quality considerations



The pipeline investigates and tracks:



\- Missing customer IDs

\- Exact duplicate rows

\- Cancellation invoices

\- Negative quantities

\- Zero and negative unit prices

\- Quarantined records and source-row traceability



Missing customer IDs, cancellations, and negative quantities are not automatically treated as invalid records. Quarantine rules and duplicate-review decisions are kept explicit.



\## PostgreSQL data model



\### Raw and analytics tables



\- `raw\_retail\_transactions` — source transaction records loaded into PostgreSQL.

\- `pipeline\_loads` — records load metadata, status, row count, and file fingerprint.

\- `retail\_transaction\_analytics` — view containing transaction line values, transaction classifications, and missing-customer indicators.



\### Dimensional warehouse



\- `dim\_product` — product stock codes and descriptions.

\- `dim\_customer` — known customers and an Unknown customer record for transactions with missing customer IDs.

\- `dim\_date` — calendar dates and year, quarter, month, and day attributes.

\- `fact\_retail\_transactions` — transaction measures and foreign keys to the product, customer, and date dimensions.



The fact table preserves source-row references and includes quantity, unit price, line value, invoice date, and transaction type.



\## Current warehouse validation



The local PostgreSQL warehouse has been populated and validated with these results:



\- \*\*Fact rows:\*\* 536,641

\- \*\*Raw rows:\*\* 536,641

\- \*\*Row-count difference:\*\* 0

\- \*\*Product dimension:\*\* 4,070 products

\- \*\*Known customer dimension records:\*\* 4,372

\- \*\*Date dimension:\*\* 305 dates

\- \*\*Transactions mapped to the Unknown customer record:\*\* 135,037

\- \*\*Missing product, customer, or date references in the fact table:\*\* 0



The transaction summary distinguishes standard transactions, cancellation invoices, and negative-quantity transactions. Line values are analytical transaction values, not audited accounting revenue.



\## Automated tests



The current test suite contains \*\*9 tests\*\*, covering:



\- Raw-table row count

\- Source-row uniqueness

\- Analytics-view consistency

\- Preservation of missing customer IDs

\- Successful load metadata and fingerprint format

\- Fact-table row count

\- Fact-table source-row uniqueness

\- Fact-table dimension references

\- Missing-customer mapping to the Unknown dimension



Run the tests from the project root with:



```bash

python -m pytest tests/test\_pipeline.py -v

```



The suite has passed locally with 9 tests. The tests currently use the configured PostgreSQL database and expected dataset row counts.



\## SQL scripts



Important SQL files include:



\- `sql/create\_raw\_table.sql`

\- `sql/create\_load\_control.sql`

\- `sql/add\_file\_fingerprint.sql`

\- `sql/data\_quality\_checks.sql`

\- `sql/create\_analytics\_view.sql`

\- `sql/monthly\_sales\_analysis.sql`

\- `sql/create\_warehouse\_schema.sql`

\- `sql/populate\_warehouse\_dimensions.sql`

\- `sql/populate\_fact\_table.sql`

\- `sql/warehouse\_integrity\_checks.sql`



The warehouse population scripts depend on the raw table being loaded first. Run them in dependency order: create the schema, populate dimensions, populate the fact table, and then run the integrity checks.



\## Configuration and security



Database settings are loaded from a local `.env` file. Configure the required database variables locally and do not commit credentials to version control.



The `.gitignore` file excludes `.env` and the Python virtual environment.



\## Current limitations and future improvements



\- Duplicate candidates require business-rule review before being classified as erroneous.

\- The current warehouse load is a local, dataset-specific workflow rather than a fully automated incremental pipeline.

\- The automated tests use fixed row-count expectations for the current dataset.

\- Cloud deployment, orchestration, monitoring, and incremental processing are potential future enhancements, not implemented capabilities.
