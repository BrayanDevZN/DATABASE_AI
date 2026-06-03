ALTER TABLE data_sources
ADD COLUMN IF NOT EXISTS source_type VARCHAR(20) NOT NULL DEFAULT 'file',
ADD COLUMN IF NOT EXISTS connection_config JSONB NOT NULL DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS refresh_interval_days INTEGER,
ADD COLUMN IF NOT EXISTS last_synced_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS next_sync_at TIMESTAMP;

UPDATE data_sources
SET source_type = COALESCE(NULLIF(source_type, ''), 'file'),
    connection_config = COALESCE(connection_config, '{}'::jsonb),
    last_synced_at = COALESCE(last_synced_at, updated_at),
    next_sync_at = CASE
        WHEN refresh_interval_days IS NULL THEN next_sync_at
        ELSE COALESCE(next_sync_at, updated_at + (refresh_interval_days || ' days')::interval)
    END;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'data_sources_source_type_check'
    ) THEN
        ALTER TABLE data_sources
        ADD CONSTRAINT data_sources_source_type_check
        CHECK (source_type IN ('file', 'web', 'database'));
    END IF;
END $$;
