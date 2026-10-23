
-- Monthly retail performance from the dimensional warehouse.
-- Cancellation and negative-quantity transactions are reported separately.
-- Line values are transaction-level values, not audited accounting revenue.

SELECT
    d.year,
    d.month,
    d.month_name,

    COUNT(*) AS total_transaction_lines,

    COUNT(*) FILTER (
        WHERE f.transaction_type = 'STANDARD'
    ) AS standard_lines,

    COUNT(*) FILTER (
        WHERE f.transaction_type = 'CANCELLATION'
    ) AS cancellation_lines,

    COUNT(*) FILTER (
        WHERE f.transaction_type = 'NEGATIVE_QUANTITY'
    ) AS negative_quantity_lines,

    ROUND(
        SUM(f.line_value) FILTER (
            WHERE f.transaction_type = 'STANDARD'
        ),
        2
    ) AS standard_line_value,

    ROUND(
        SUM(f.line_value) FILTER (
            WHERE f.transaction_type = 'CANCELLATION'
        ),
        2
    ) AS cancellation_line_value,

    ROUND(
        SUM(f.line_value) FILTER (
            WHERE f.transaction_type = 'NEGATIVE_QUANTITY'
        ),
        2
    ) AS negative_quantity_line_value,

    ROUND(SUM(f.line_value), 2) AS net_line_value

FROM fact_retail_transactions AS f
JOIN dim_date AS d
    ON f.date_key = d.date_key

GROUP BY
    d.year,
    d.month,
    d.month_name

ORDER BY
    d.year,
    d.month;
