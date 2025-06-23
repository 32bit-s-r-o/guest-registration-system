-- Migration: 1.6.0 - Add Housekeeping Photo Support
-- Created: 2025-06-23T00:00:06
-- Description: Add support for multiple photos per housekeeping task

-- Up Migration
CREATE TABLE IF NOT EXISTS guest_reg_housekeeping_photo (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES guest_reg_housekeeping(id) ON DELETE CASCADE,
    file_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_housekeeping_photo_task_id ON guest_reg_housekeeping_photo(task_id);

-- Down Migration (Rollback)
DROP INDEX IF EXISTS idx_housekeeping_photo_task_id;
DROP TABLE IF EXISTS guest_reg_housekeeping_photo; 