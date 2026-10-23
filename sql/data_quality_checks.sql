
-- 1. Overall row count and source-row uniqueness
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT source_row_number) AS unique_source_rows
FROM raw_retail_transactions;

-- 2. Transaction-quality indicators
SELECT
    COUNT(*) FILTER (WHERE quantity < 0) AS negative_quantity_rows,
    COUNT(*) FILTER (WHERE unit_price = 0) AS zero_price_rows,
    COUNT(*) FILTER (WHERE unit_price < 0) AS negative_price_rows,
    COUNT(*) FILTER (WHERE customer_id IS NULL) AS missing_customer_ids,
    COUNT(*) FILTER (WHERE invoice_no LIKE 'C%') AS cancellation_invoice_rows
FROM raw_retail_transactions;

-- 3. Transaction date range
SELECT
    MIN(invoice_date) AS earliest_transaction,
    MAX(invoice_date) AS latest_transaction
FROM raw_retail_transactions;
