
CREATE TABLE IF NOT EXISTS pipeline_loads (
    load_name       VARCHAR(100) PRIMARY KEY,
    source_file     VARCHAR(255) NOT NULL,
    rows_loaded     INTEGER NOT NULL,
    load_status     VARCHAR(20) NOT NULL,
    loaded_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
