
-- Monthly retail transaction analysis
-- Values are line-level measures, not audited accounting revenue.

SELECT
    DATE_TRUNC('month', invoice_date)::DATE AS sales_month,
    COUNT(*) AS transaction_lines,

    ROUND(SUM(line_value), 2) AS net_line_value,

    ROUND(
        SUM(
            CASE
                WHEN quantity > 0
                     AND invoice_no NOT LIKE 'C%'
                THEN line_value
                ELSE 0
            END
        ),
        2
    ) AS positive_sales_line_value,

    ROUND(
        SUM(
            CASE
                WHEN quantity < 0
                     OR invoice_no LIKE 'C%'
                THEN line_value
                ELSE 0
            END
        ),
        2
    ) AS return_cancellation_line_value

FROM retail_transaction_analytics
GROUP BY DATE_TRUNC('month', invoice_date)::DATE
ORDER BY sales_month;
