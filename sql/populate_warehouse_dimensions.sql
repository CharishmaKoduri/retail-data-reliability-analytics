
-- Populate product dimension
INSERT INTO dim_product (stock_code, description)
SELECT
    stock_code,
    MAX(description) AS description
FROM raw_retail_transactions
WHERE stock_code IS NOT NULL
GROUP BY stock_code
ON CONFLICT (stock_code)
DO UPDATE SET description = EXCLUDED.description;


-- Populate customer dimension
-- Reserve NULL customer_id for unknown/missing customers.
INSERT INTO dim_customer (customer_id, country)
SELECT
    customer_id,
    MAX(country) AS country
FROM raw_retail_transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ON CONFLICT (customer_id)
DO UPDATE SET country = EXCLUDED.country;

INSERT INTO dim_customer (customer_id, country)
VALUES (NULL, 'Unknown')
ON CONFLICT DO NOTHING;


-- Populate date dimension
INSERT INTO dim_date (
    date_key, full_date, year, quarter,
    month, month_name, day_of_month
)
SELECT DISTINCT
    TO_CHAR(invoice_date::date, 'YYYYMMDD')::INTEGER,
    invoice_date::date,
    EXTRACT(YEAR FROM invoice_date)::SMALLINT,
    EXTRACT(QUARTER FROM invoice_date)::SMALLINT,
    EXTRACT(MONTH FROM invoice_date)::SMALLINT,
    TO_CHAR(invoice_date, 'FMMonth'),
    EXTRACT(DAY FROM invoice_date)::SMALLINT
FROM raw_retail_transactions
WHERE invoice_date IS NOT NULL
ON CONFLICT (date_key) DO NOTHING;
