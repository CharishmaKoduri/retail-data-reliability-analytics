
-- 1. Product dimension
CREATE TABLE IF NOT EXISTS dim_product (
    product_key  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    stock_code   VARCHAR(20) NOT NULL UNIQUE,
    description  TEXT
);

-- 2. Customer dimension
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id  INTEGER UNIQUE,
    country      VARCHAR(100)
);

-- 3. Date dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key     INTEGER PRIMARY KEY,
    full_date    DATE NOT NULL UNIQUE,
    year         SMALLINT NOT NULL,
    quarter      SMALLINT NOT NULL,
    month        SMALLINT NOT NULL,
    month_name   VARCHAR(10) NOT NULL,
    day_of_month SMALLINT NOT NULL
);

-- 4. Retail transaction fact table
CREATE TABLE IF NOT EXISTS fact_retail_transactions (
    transaction_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,

    source_row_number INTEGER NOT NULL UNIQUE,
    invoice_no       VARCHAR(20),

    product_key      INTEGER NOT NULL
        REFERENCES dim_product(product_key),

    customer_key     INTEGER
        REFERENCES dim_customer(customer_key),

    date_key         INTEGER NOT NULL
        REFERENCES dim_date(date_key),

    invoice_date     TIMESTAMP NOT NULL,
    quantity         INTEGER NOT NULL,
    unit_price       NUMERIC(12, 4) NOT NULL,
    line_value       NUMERIC(14, 4) NOT NULL,

    transaction_type VARCHAR(30) NOT NULL
);

-- 5. Indexes for common analytical queries
CREATE INDEX IF NOT EXISTS idx_fact_invoice_no
    ON fact_retail_transactions(invoice_no);

CREATE INDEX IF NOT EXISTS idx_fact_product_key
    ON fact_retail_transactions(product_key);

CREATE INDEX IF NOT EXISTS idx_fact_customer_key
    ON fact_retail_transactions(customer_key);

CREATE INDEX IF NOT EXISTS idx_fact_date_key
    ON fact_retail_transactions(date_key);

CREATE INDEX IF NOT EXISTS idx_fact_invoice_date
    ON fact_retail_transactions(invoice_date);
