-- Migration: 1.0.0 - initial_schema
-- Created: 2025-01-01T00:00:00
-- Up Migration
CREATE TABLE IF NOT EXISTS guest_reg_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    airbnb_listing_id VARCHAR(100),
    airbnb_calendar_url TEXT,
    airbnb_sync_enabled BOOLEAN DEFAULT FALSE,
    airbnb_last_sync TIMESTAMP,
    company_name VARCHAR(200),
    company_ico VARCHAR(50),
    company_vat VARCHAR(50),
    contact_name VARCHAR(200),
    contact_phone VARCHAR(50),
    contact_address TEXT,
    contact_website VARCHAR(200),
    contact_description TEXT,
    photo_required_adults BOOLEAN DEFAULT TRUE,
    photo_required_children BOOLEAN DEFAULT TRUE,
    custom_line_1 VARCHAR(200),
    custom_line_2 VARCHAR(200),
    custom_line_3 VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS guest_reg_trip (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    max_guests INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_id INTEGER REFERENCES guest_reg_user(id) NOT NULL,
    airbnb_reservation_id VARCHAR(100) UNIQUE,
    airbnb_guest_name VARCHAR(200),
    airbnb_guest_email VARCHAR(200),
    airbnb_guest_count INTEGER,
    airbnb_synced_at TIMESTAMP,
    is_airbnb_synced BOOLEAN DEFAULT FALSE,
    airbnb_confirm_code VARCHAR(50) UNIQUE
);

CREATE TABLE IF NOT EXISTS guest_reg_registration (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES guest_reg_trip(id) NOT NULL,
    email VARCHAR(120) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    admin_comment TEXT,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guest_reg_guest (
    id SERIAL PRIMARY KEY,
    registration_id INTEGER REFERENCES guest_reg_registration(id) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    age_category VARCHAR(20) NOT NULL DEFAULT 'adult',
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100) NOT NULL,
    document_image VARCHAR(255),
    gdpr_consent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guest_reg_invoice (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    admin_id INTEGER REFERENCES guest_reg_user(id) NOT NULL,
    registration_id INTEGER REFERENCES guest_reg_registration(id),
    client_name VARCHAR(200) NOT NULL,
    client_email VARCHAR(200),
    client_vat_number VARCHAR(50),
    client_address TEXT,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    due_date DATE,
    subtotal NUMERIC(10, 2) DEFAULT 0,
    vat_total NUMERIC(10, 2) DEFAULT 0,
    total_amount NUMERIC(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'EUR',
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guest_reg_invoice_item (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER REFERENCES guest_reg_invoice(id) NOT NULL,
    description VARCHAR(500) NOT NULL,
    quantity NUMERIC(10, 2) DEFAULT 1,
    unit_price NUMERIC(10, 2) NOT NULL,
    vat_rate NUMERIC(5, 2) DEFAULT 0,
    line_total NUMERIC(10, 2) DEFAULT 0,
    vat_amount NUMERIC(10, 2) DEFAULT 0,
    total_with_vat NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guest_reg_housekeeping (
    id SERIAL PRIMARY KEY,
    trip_id INTEGER REFERENCES guest_reg_trip(id) NOT NULL,
    housekeeper_id INTEGER REFERENCES guest_reg_user(id) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    pay_amount NUMERIC(10, 2) DEFAULT 0,
    paid BOOLEAN DEFAULT FALSE,
    paid_date TIMESTAMP,
    amenity_photo_path VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Down Migration (Rollback)
DROP TABLE IF EXISTS guest_reg_housekeeping CASCADE;
DROP TABLE IF EXISTS guest_reg_invoice_item CASCADE;
DROP TABLE IF EXISTS guest_reg_invoice CASCADE;
DROP TABLE IF EXISTS guest_reg_guest CASCADE;
DROP TABLE IF EXISTS guest_reg_registration CASCADE;
DROP TABLE IF EXISTS guest_reg_trip CASCADE;
DROP TABLE IF EXISTS guest_reg_user CASCADE; 