
CREATE OR REPLACE VIEW retail_transaction_analytics AS
SELECT
    source_row_number,
    invoice_no,
    stock_code,
    description,
    quantity,
    invoice_date,
    unit_price,
    customer_id,
    country,
    quantity * unit_price AS line_value,
    CASE
        WHEN invoice_no LIKE 'C%' THEN 'CANCELLATION'
        WHEN quantity < 0 THEN 'NEGATIVE_QUANTITY'
        ELSE 'STANDARD'
    END AS transaction_type,
    CASE
        WHEN customer_id IS NULL THEN TRUE
        ELSE FALSE
    END AS missing_customer_id
FROM raw_retail_transactions;
