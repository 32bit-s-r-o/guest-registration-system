-- Migration: Add is_deleted column to user table for soft delete support
-- Version: 1.5.0
-- Date: 2025-06-23

-- Up Migration
ALTER TABLE guest_reg_user ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE;

-- Down Migration (Rollback)
ALTER TABLE guest_reg_user DROP COLUMN IF EXISTS is_deleted; 