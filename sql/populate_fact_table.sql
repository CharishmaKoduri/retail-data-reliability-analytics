
-- Load retail transactions into the warehouse fact table.
-- Preserve cancellations, returns, and missing customer IDs.

INSERT INTO fact_retail_transactions (
    source_row_number,
    invoice_no,
    product_key,
    customer_key,
    date_key,
    invoice_date,
    quantity,
    unit_price,
    line_value,
    transaction_type
)
SELECT
    r.source_row_number,
    r.invoice_no,
    p.product_key,
    COALESCE(c.customer_key, unknown_c.customer_key),
    d.date_key,
    r.invoice_date,
    r.quantity,
    r.unit_price,
    r.quantity::NUMERIC * r.unit_price,
    CASE
        WHEN r.invoice_no LIKE 'C%' THEN 'CANCELLATION'
        WHEN r.quantity < 0 THEN 'NEGATIVE_QUANTITY'
        ELSE 'STANDARD'
    END
FROM raw_retail_transactions AS r
JOIN dim_product AS p
    ON p.stock_code = r.stock_code
JOIN dim_date AS d
    ON d.full_date = r.invoice_date::date
LEFT JOIN dim_customer AS c
    ON c.customer_id = r.customer_id
CROSS JOIN dim_customer AS unknown_c
WHERE
    unknown_c.customer_id IS NULL
    AND (r.customer_id IS NULL OR c.customer_key IS NOT NULL)
ON CONFLICT (source_row_number) DO NOTHING;
