-- Up Migration
-- Migration: 1.8.0_add_default_housekeeper_pay
-- Description: Add default housekeeper pay setting to user table
-- Date: 2025-06-23

-- Add default_housekeeper_pay to user table
ALTER TABLE guest_reg_user ADD COLUMN IF NOT EXISTS default_housekeeper_pay NUMERIC(10,2) NOT NULL DEFAULT 20;

-- Down Migration (Rollback)
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS default_housekeeper_pay;

-- Version tracking is handled automatically by the migration system 