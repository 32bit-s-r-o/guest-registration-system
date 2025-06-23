-- Migration: 1.1.0 - add_performance_indexes
-- Created: 2025-01-01T00:00:01
-- Up Migration
-- Add performance indexes
CREATE INDEX IF NOT EXISTS idx_trip_admin_id ON guest_reg_trip(admin_id);
CREATE INDEX IF NOT EXISTS idx_trip_dates ON guest_reg_trip(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_registration_trip_id ON guest_reg_registration(trip_id);
CREATE INDEX IF NOT EXISTS idx_registration_status ON guest_reg_registration(status);
CREATE INDEX IF NOT EXISTS idx_registration_created_at ON guest_reg_registration(created_at);
CREATE INDEX IF NOT EXISTS idx_guest_registration_id ON guest_reg_guest(registration_id);
CREATE INDEX IF NOT EXISTS idx_invoice_admin_id ON guest_reg_invoice(admin_id);
CREATE INDEX IF NOT EXISTS idx_invoice_registration_id ON guest_reg_invoice(registration_id);
CREATE INDEX IF NOT EXISTS idx_invoice_status ON guest_reg_invoice(status);
CREATE INDEX IF NOT EXISTS idx_housekeeping_trip_id ON guest_reg_housekeeping(trip_id);
CREATE INDEX IF NOT EXISTS idx_housekeeping_housekeeper_id ON guest_reg_housekeeping(housekeeper_id);
CREATE INDEX IF NOT EXISTS idx_housekeeping_date ON guest_reg_housekeeping(date);

-- Down Migration (Rollback)
-- Drop performance indexes
DROP INDEX IF EXISTS idx_trip_admin_id;
DROP INDEX IF EXISTS idx_trip_dates;
DROP INDEX IF EXISTS idx_registration_trip_id;
DROP INDEX IF EXISTS idx_registration_status;
DROP INDEX IF EXISTS idx_registration_created_at;
DROP INDEX IF EXISTS idx_guest_registration_id;
DROP INDEX IF EXISTS idx_invoice_admin_id;
DROP INDEX IF EXISTS idx_invoice_registration_id;
DROP INDEX IF EXISTS idx_invoice_status;
DROP INDEX IF EXISTS idx_housekeeping_trip_id;
DROP INDEX IF EXISTS idx_housekeeping_housekeeper_id;
DROP INDEX IF EXISTS idx_housekeeping_date; 