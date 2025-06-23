-- Migration: 1.4.0 - Add Amenity-Housekeeper System
-- Date: 2025-01-01
-- Description: Add support for multiple housekeepers per amenity with default assignment

-- Up Migration
-- Create amenity_housekeeper junction table
CREATE TABLE IF NOT EXISTS guest_reg_amenity_housekeeper (
    id SERIAL PRIMARY KEY,
    amenity_id INTEGER NOT NULL,
    housekeeper_id INTEGER NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (amenity_id) REFERENCES guest_reg_amenity(id) ON DELETE CASCADE,
    FOREIGN KEY (housekeeper_id) REFERENCES guest_reg_user(id) ON DELETE CASCADE,
    UNIQUE(amenity_id, housekeeper_id)
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_amenity_housekeeper_amenity ON guest_reg_amenity_housekeeper(amenity_id);
CREATE INDEX IF NOT EXISTS idx_amenity_housekeeper_housekeeper ON guest_reg_amenity_housekeeper(housekeeper_id);
CREATE INDEX IF NOT EXISTS idx_amenity_housekeeper_default ON guest_reg_amenity_housekeeper(amenity_id, is_default);

-- Add default_housekeeper_id to amenity table for backward compatibility
ALTER TABLE guest_reg_amenity ADD COLUMN default_housekeeper_id INTEGER REFERENCES guest_reg_user(id);

-- Triggers for single default (Postgres version would require a function, skipping for now)

-- Down Migration
DROP INDEX IF EXISTS idx_amenity_housekeeper_default;
DROP INDEX IF EXISTS idx_amenity_housekeeper_housekeeper;
DROP INDEX IF EXISTS idx_amenity_housekeeper_amenity;
DROP TABLE IF EXISTS guest_reg_amenity_housekeeper;
-- Note: PostgreSQL doesn't support DROP COLUMN IF EXISTS in all versions, so we'll leave the column for backward compatibility 