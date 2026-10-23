
ALTER TABLE pipeline_loads
ADD COLUMN IF NOT EXISTS file_sha256 CHAR(64);
