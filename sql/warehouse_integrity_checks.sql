
-- 1. Raw versus fact row counts
SELECT
    (SELECT COUNT(*) FROM raw_retail_transactions) AS raw_rows,
    (SELECT COUNT(*) FROM fact_retail_transactions) AS fact_rows,
    (SELECT COUNT(*) FROM raw_retail_transactions)
      - (SELECT COUNT(*) FROM fact_retail_transactions) AS row_difference;

-- 2. Duplicate source rows in the fact table
SELECT source_row_number, COUNT(*) AS occurrences
FROM fact_retail_transactions
GROUP BY source_row_number
HAVING COUNT(*) > 1;

-- 3. Orphaned dimension references
SELECT
    COUNT(*) FILTER (WHERE p.product_key IS NULL) AS missing_products,
    COUNT(*) FILTER (WHERE c.customer_key IS NULL) AS missing_customers,
    COUNT(*) FILTER (WHERE d.date_key IS NULL) AS missing_dates
FROM fact_retail_transactions f
LEFT JOIN dim_product p ON f.product_key = p.product_key
LEFT JOIN dim_customer c ON f.customer_key = c.customer_key
LEFT JOIN dim_date d ON f.date_key = d.date_key;

-- 4. Transaction counts and line values
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(line_value), 2) AS total_line_value
FROM fact_retail_transactions
GROUP BY transaction_type
ORDER BY transaction_type;

-- 5. Find raw transactions missing from the fact table
SELECT COUNT(*) AS missing_fact_rows
FROM raw_retail_transactions r
LEFT JOIN fact_retail_transactions f
    ON f.source_row_number = r.source_row_number
WHERE f.source_row_number IS NULL;

-- 6. Compare raw and fact transaction values
-- This checks key source fields and the calculated line value.
SELECT COUNT(*) AS mismatched_transactions
FROM raw_retail_transactions r
JOIN fact_retail_transactions f
    ON f.source_row_number = r.source_row_number
WHERE f.invoice_no IS DISTINCT FROM r.invoice_no
   OR f.invoice_date IS DISTINCT FROM r.invoice_date
   OR f.quantity IS DISTINCT FROM r.quantity
   OR f.unit_price IS DISTINCT FROM r.unit_price
   OR f.line_value IS DISTINCT FROM
      (r.quantity::NUMERIC * r.unit_price);
