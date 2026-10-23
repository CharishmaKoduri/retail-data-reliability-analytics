
CREATE TABLE IF NOT EXISTS raw_retail_transactions (
    source_row_number INTEGER PRIMARY KEY,
    invoice_no        VARCHAR(20),
    stock_code        VARCHAR(20),
    description       TEXT,
    quantity          INTEGER,
    invoice_date      TIMESTAMP,
    unit_price        NUMERIC(12, 4),
    customer_id       INTEGER,
    country           VARCHAR(100)
);
