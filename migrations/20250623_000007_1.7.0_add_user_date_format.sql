-- Migration: 1.7.0 - Add User Date Format
-- Created: 2025-06-23T00:00:07
-- Description: Add date_format column to user table for preferred date display

-- Up Migration
ALTER TABLE guest_reg_user ADD COLUMN IF NOT EXISTS date_format VARCHAR(32) DEFAULT 'd.m.Y';

-- Down Migration (Rollback)
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS date_format; 