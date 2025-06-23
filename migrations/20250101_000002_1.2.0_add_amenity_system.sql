-- Up Migration
-- Migration: Add Amenity System
-- Version: 1.2.0
-- Description: Add amenity management system with individual calendar URLs and guest limits

-- Create amenity table
CREATE TABLE IF NOT EXISTS guest_reg_amenity (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    max_guests INTEGER NOT NULL DEFAULT 1,
    admin_id INTEGER NOT NULL REFERENCES guest_reg_user(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    airbnb_listing_id VARCHAR(100),
    airbnb_calendar_url TEXT,
    airbnb_sync_enabled BOOLEAN DEFAULT FALSE,
    airbnb_last_sync TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Add amenity_id to trip table
ALTER TABLE guest_reg_trip ADD COLUMN IF NOT EXISTS amenity_id INTEGER REFERENCES guest_reg_amenity(id) ON DELETE CASCADE;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_amenity_admin_id ON guest_reg_amenity(admin_id);
CREATE INDEX IF NOT EXISTS idx_amenity_active ON guest_reg_amenity(is_active);
CREATE INDEX IF NOT EXISTS idx_trip_amenity_id ON guest_reg_trip(amenity_id);

-- Migrate existing data (if any)
-- This will create a default amenity for existing users and assign existing trips to it
INSERT INTO guest_reg_amenity (name, description, max_guests, admin_id, airbnb_listing_id, airbnb_calendar_url, airbnb_sync_enabled, airbnb_last_sync, is_active)
SELECT 
    'Default Amenity' as name,
    'Default amenity created during migration' as description,
    4 as max_guests,
    id as admin_id,
    airbnb_listing_id,
    airbnb_calendar_url,
    airbnb_sync_enabled,
    airbnb_last_sync,
    TRUE as is_active
FROM guest_reg_user
WHERE role = 'admin'
ON CONFLICT DO NOTHING;

-- Update existing trips to use the default amenity
UPDATE guest_reg_trip 
SET amenity_id = (
    SELECT a.id 
    FROM guest_reg_amenity a 
    WHERE a.admin_id = guest_reg_trip.admin_id 
    LIMIT 1
)
WHERE amenity_id IS NULL;

-- Make amenity_id NOT NULL after migration
ALTER TABLE guest_reg_trip ALTER COLUMN amenity_id SET NOT NULL;

-- Remove old Airbnb fields from user table (they're now in amenity table)
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS airbnb_listing_id;
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS airbnb_calendar_url;
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS airbnb_sync_enabled;
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS airbnb_last_sync; 