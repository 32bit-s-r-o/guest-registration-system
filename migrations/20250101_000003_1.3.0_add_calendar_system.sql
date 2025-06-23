-- Up Migration
-- Migration: 1.3.0_add_calendar_system
-- Description: Add Calendar table and update Trip table for multi-calendar support
-- Date: 2025-01-01

-- Create Calendar table
CREATE TABLE IF NOT EXISTS guest_reg_calendar (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    amenity_id INTEGER NOT NULL REFERENCES guest_reg_amenity(id) ON DELETE CASCADE,
    calendar_url TEXT NOT NULL,
    calendar_type VARCHAR(50) DEFAULT 'airbnb',
    sync_enabled BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP,
    sync_frequency VARCHAR(20) DEFAULT 'daily',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for Calendar table
CREATE INDEX IF NOT EXISTS idx_calendar_amenity_id ON guest_reg_calendar(amenity_id);
CREATE INDEX IF NOT EXISTS idx_calendar_sync_enabled ON guest_reg_calendar(sync_enabled);
CREATE INDEX IF NOT EXISTS idx_calendar_is_active ON guest_reg_calendar(is_active);
CREATE INDEX IF NOT EXISTS idx_calendar_type ON guest_reg_calendar(calendar_type);

-- Add new columns to Trip table
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS calendar_id INTEGER REFERENCES guest_reg_calendar(id);
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS external_reservation_id VARCHAR(100) UNIQUE;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS external_guest_name VARCHAR(200);
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS external_guest_email VARCHAR(200);
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS external_guest_count INTEGER;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS external_synced_at TIMESTAMP;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS is_externally_synced BOOLEAN DEFAULT FALSE;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS external_confirm_code VARCHAR(50) UNIQUE;

-- Add indexes for new Trip columns
CREATE INDEX IF NOT EXISTS idx_trip_calendar_id ON guest_reg_trip(calendar_id);
CREATE INDEX IF NOT EXISTS idx_trip_external_reservation_id ON guest_reg_trip(external_reservation_id);
CREATE INDEX IF NOT EXISTS idx_trip_external_confirm_code ON guest_reg_trip(external_confirm_code);
CREATE INDEX IF NOT EXISTS idx_trip_is_externally_synced ON guest_reg_trip(is_externally_synced);

-- Migrate existing Airbnb data to new structure
-- First, create a default calendar for each amenity that has Airbnb settings
INSERT INTO guest_reg_calendar (name, description, amenity_id, calendar_url, calendar_type, sync_enabled, last_sync, sync_frequency, is_active, created_at, updated_at)
SELECT 
    'Airbnb Calendar' as name,
    'Migrated from existing Airbnb settings' as description,
    id as amenity_id,
    airbnb_calendar_url as calendar_url,
    'airbnb' as calendar_type,
    airbnb_sync_enabled as sync_enabled,
    airbnb_last_sync as last_sync,
    'daily' as sync_frequency,
    is_active,
    created_at,
    updated_at
FROM guest_reg_amenity 
WHERE airbnb_calendar_url IS NOT NULL AND airbnb_calendar_url != '';

-- Update existing trips to use the new external fields
UPDATE guest_reg_trip 
SET 
    calendar_id = (
        SELECT c.id 
        FROM guest_reg_calendar c 
        WHERE c.amenity_id = guest_reg_trip.amenity_id 
        AND c.calendar_type = 'airbnb'
        LIMIT 1
    ),
    external_reservation_id = airbnb_reservation_id,
    external_guest_name = airbnb_guest_name,
    external_guest_email = airbnb_guest_email,
    external_guest_count = airbnb_guest_count,
    external_synced_at = airbnb_synced_at,
    is_externally_synced = is_airbnb_synced,
    external_confirm_code = airbnb_confirm_code
WHERE airbnb_reservation_id IS NOT NULL OR airbnb_confirm_code IS NOT NULL;

-- Remove old Airbnb columns from Amenity table
ALTER TABLE guest_reg_amenity DROP COLUMN IF EXISTS airbnb_listing_id;
ALTER TABLE guest_reg_amenity DROP COLUMN IF EXISTS airbnb_calendar_url;
ALTER TABLE guest_reg_amenity DROP COLUMN IF EXISTS airbnb_sync_enabled;
ALTER TABLE guest_reg_amenity DROP COLUMN IF EXISTS airbnb_last_sync;

-- Remove old Airbnb columns from Trip table
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS airbnb_reservation_id;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS airbnb_guest_name;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS airbnb_guest_email;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS airbnb_guest_count;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS airbnb_synced_at;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS is_airbnb_synced;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS airbnb_confirm_code;

-- Down Migration (Rollback)
DROP INDEX IF EXISTS idx_trip_is_externally_synced;
DROP INDEX IF EXISTS idx_trip_external_confirm_code;
DROP INDEX IF EXISTS idx_trip_external_reservation_id;
DROP INDEX IF EXISTS idx_trip_calendar_id;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS calendar_id;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS external_reservation_id;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS external_guest_name;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS external_guest_email;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS external_guest_count;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS external_synced_at;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS is_externally_synced;
ALTER TABLE guest_reg_trip DROP COLUMN IF EXISTS external_confirm_code;
DROP INDEX IF EXISTS idx_calendar_type;
DROP INDEX IF EXISTS idx_calendar_is_active;
DROP INDEX IF EXISTS idx_calendar_sync_enabled;
DROP INDEX IF EXISTS idx_calendar_amenity_id;
DROP TABLE IF EXISTS guest_reg_calendar;
-- Optionally, re-add old Airbnb columns to amenity and trip tables (if needed for rollback)
ALTER TABLE guest_reg_amenity ADD COLUMN IF NOT EXISTS airbnb_listing_id VARCHAR(100);
ALTER TABLE guest_reg_amenity ADD COLUMN IF NOT EXISTS airbnb_calendar_url TEXT;
ALTER TABLE guest_reg_amenity ADD COLUMN IF NOT EXISTS airbnb_sync_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE guest_reg_amenity ADD COLUMN IF NOT EXISTS airbnb_last_sync TIMESTAMP;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS airbnb_reservation_id VARCHAR(100);
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS airbnb_guest_name VARCHAR(200);
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS airbnb_guest_email VARCHAR(200);
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS airbnb_guest_count INTEGER;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS airbnb_synced_at TIMESTAMP;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS is_airbnb_synced BOOLEAN DEFAULT FALSE;
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS airbnb_confirm_code VARCHAR(50);

-- Version tracking is handled automatically by the migration system 