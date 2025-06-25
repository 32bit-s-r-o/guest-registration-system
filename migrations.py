#!/usr/bin/env python3
"""
Database Migration System for Guest Registration System
Handles versioning, migrations, and rollbacks
"""

import os
import sys
import json
from datetime import datetime
import subprocess
import tempfile
import shutil
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
from config import Config

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
TABLE_PREFIX = os.getenv('TABLE_PREFIX', 'guest_reg_')

class MigrationManager:
    def __init__(self, database_url=None, table_prefix=None):
        self.database_url = database_url or DATABASE_URL
        self.table_prefix = table_prefix or TABLE_PREFIX
        self.migrations_dir = 'migrations'
        self.version_file = os.path.join(self.migrations_dir, 'version.json')
        self.migrations_table = f"{self.table_prefix}migrations"
        
        # Create database engine
        self.engine = create_engine(self.database_url)
        
        # Ensure migrations directory exists
        os.makedirs(self.migrations_dir, exist_ok=True)
        
        # Initialize migrations table
        self._init_migrations_table()
    
    def _init_migrations_table(self):
        """Initialize the migrations tracking table"""
        # Check if migrations table exists
        inspector = inspect(self.engine)
        if self.migrations_table not in inspector.get_table_names():
            # Create migrations table
            create_table_sql = f"""
            CREATE TABLE {self.migrations_table} (
                id SERIAL PRIMARY KEY,
                version VARCHAR(50) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum VARCHAR(64),
                rollback_sql TEXT
            );
            """
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            print(f"✅ Created migrations table: {self.migrations_table}")
    
    def get_current_version(self):
        """Get current database version"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT version FROM {self.migrations_table} ORDER BY applied_at DESC LIMIT 1")
                ).fetchone()
                return result[0] if result else "0.0.0"
        except Exception as e:
            print(f"⚠️ Could not get current version: {e}")
            return "0.0.0"
    
    def get_applied_migrations(self):
        """Get list of applied migrations"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT version, name, applied_at FROM {self.migrations_table} ORDER BY applied_at")
                ).fetchall()
                return [{"version": row[0], "name": row[1], "applied_at": row[2]} for row in result]
        except Exception as e:
            print(f"⚠️ Could not get applied migrations: {e}")
            return []
    
    def create_migration(self, version, name, up_sql, down_sql=None):
        """Create a new migration file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{version}_{name}.sql"
        filepath = os.path.join(self.migrations_dir, filename)
        
        migration_content = f"""-- Migration: {version} - {name}
-- Created: {datetime.now().isoformat()}
-- Up Migration
{up_sql}

-- Down Migration (Rollback)
{down_sql or '-- No rollback available'}
"""
        
        with open(filepath, 'w') as f:
            f.write(migration_content)
        
        print(f"✅ Created migration: {filename}")
        return filepath
    
    def apply_migration(self, version, name, sql_content, rollback_sql=None):
        """Apply a migration to the database"""
        try:
            # Detect if using SQLite
            is_sqlite = self.engine.url.get_backend_name() == 'sqlite'
            with self.engine.connect() as conn:
                if is_sqlite:
                    raw_conn = conn.connection
                    import re
                    # Split into statements
                    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                    for stmt in statements:
                        # Debug output for CREATE TABLE
                        if stmt.upper().startswith('CREATE TABLE'):
                            print(f"[DEBUG] Attempting: {stmt[:80]}...")
                        # Check for ALTER TABLE ... ADD COLUMN ...
                        alter_match = re.match(r"ALTER TABLE (\w+) ADD COLUMN (.+)", stmt, re.IGNORECASE)
                        if alter_match:
                            table, col_def = alter_match.group(1), alter_match.group(2)
                            col_name = col_def.split()[0]
                            pragma = f"PRAGMA table_info({table});"
                            cur = raw_conn.execute(pragma)
                            columns = [row[1] for row in cur.fetchall()]
                            if col_name in columns:
                                print(f"⚠️  Skipping duplicate column {col_name} on table {table} (SQLite)")
                                continue
                            col_def_sqlite = re.sub(r'UNIQUE', '', col_def, flags=re.IGNORECASE)
                            col_def_sqlite = re.sub(r'REFERENCES [^ )]+(\([^)]*\))?( ON DELETE [A-Z]+)?', '', col_def_sqlite, flags=re.IGNORECASE)
                            stmt_sqlite = f"ALTER TABLE {table} ADD COLUMN {col_def_sqlite.strip()}"
                            try:
                                print(f"[DEBUG] Attempting: {stmt_sqlite}")
                                raw_conn.execute(stmt_sqlite)
                            except Exception as e:
                                print(f"⚠️  SQLite statement failed: {stmt_sqlite}\n   {e}")
                            continue
                        # Check for CREATE INDEX ... ON ... (col)
                        index_match = re.match(r"CREATE INDEX IF NOT EXISTS (\w+) ON (\w+)\((\w+)\)", stmt, re.IGNORECASE)
                        if index_match:
                            idx_name, table, col = index_match.groups()
                            pragma = f"PRAGMA table_info({table});"
                            cur = raw_conn.execute(pragma)
                            columns = [row[1] for row in cur.fetchall()]
                            if col not in columns:
                                print(f"⚠️  Skipping index {idx_name} on missing column {col} in table {table} (SQLite)")
                                continue
                        # Otherwise, try to execute
                        try:
                            raw_conn.execute(stmt)
                        except Exception as e:
                            print(f"⚠️  SQLite statement failed: {stmt}\n   {e}")
                else:
                    # Execute the migration SQL (Postgres, etc.)
                    conn.execute(text(sql_content))
                # Record the migration
                checksum = self._calculate_checksum(sql_content)
                insert_sql = f"""
                INSERT INTO {self.migrations_table} (version, name, checksum, rollback_sql)
                VALUES (:version, :name, :checksum, :rollback_sql)
                """
                conn.execute(text(insert_sql), {
                    'version': version,
                    'name': name,
                    'checksum': checksum,
                    'rollback_sql': rollback_sql
                })
                conn.commit()
            print(f"✅ Applied migration: {version} - {name}")
            return True
        except Exception as e:
            print(f"❌ Failed to apply migration {version}: {e}")
            return False
    
    def rollback_migration(self, version):
        """Rollback a specific migration"""
        try:
            with self.engine.connect() as conn:
                # Get migration details
                result = conn.execute(
                    text(f"SELECT name, rollback_sql FROM {self.migrations_table} WHERE version = :version"),
                    {'version': version}
                ).fetchone()
                
                if not result:
                    print(f"❌ Migration {version} not found")
                    return False
                
                name, rollback_sql = result
                
                if not rollback_sql or rollback_sql.strip() == '-- No rollback available':
                    print(f"❌ No rollback available for migration {version}")
                    return False
                
                # Execute rollback
                conn.execute(text(rollback_sql))
                
                # Remove migration record
                conn.execute(
                    text(f"DELETE FROM {self.migrations_table} WHERE version = :version"),
                    {'version': version}
                )
                conn.commit()
                
            print(f"✅ Rolled back migration: {version} - {name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback migration {version}: {e}")
            return False
    
    def _calculate_checksum(self, content):
        """Calculate checksum for migration content"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_pending_migrations(self):
        """Get list of pending migrations (files that haven't been applied)"""
        applied = {m['version'] for m in self.get_applied_migrations()}
        pending = []
        
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.sql') and not filename.startswith('.'):
                # Extract version from filename: timestamp_version_name.sql
                parts = filename.replace('.sql', '').split('_')
                if len(parts) >= 3:
                    version = parts[1]  # version is second part
                    if version not in applied:
                        pending.append(filename)
        
        return sorted(pending)
    
    def migrate(self, target_version=None):
        """Run all pending migrations up to target version"""
        pending = self.get_pending_migrations()
        
        if not pending:
            print("✅ No pending migrations")
            return True
        
        print(f"🔄 Found {len(pending)} pending migrations")
        
        for filename in pending:
            if target_version and self._extract_version(filename) > target_version:
                break
                
            if not self._apply_migration_file(filename):
                print(f"❌ Migration failed at {filename}")
                return False
        
        print("✅ All migrations completed successfully")
        return True
    
    def _extract_version(self, filename):
        """Extract version from migration filename"""
        parts = filename.replace('.sql', '').split('_')
        return parts[1] if len(parts) >= 3 else "0.0.0"
    
    def _apply_migration_file(self, filename):
        """Apply a migration from file"""
        filepath = os.path.join(self.migrations_dir, filename)
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Parse migration content
        parts = content.split('-- Down Migration (Rollback)')
        up_sql = parts[0].split('-- Up Migration', 1)[1].strip()
        down_sql = parts[1].strip() if len(parts) > 1 else None
        
        # Replace hardcoded prefix with actual table prefix
        up_sql = up_sql.replace('guest_reg_', self.table_prefix)
        if down_sql:
            down_sql = down_sql.replace('guest_reg_', self.table_prefix)
        
        # Detect if using SQLite and convert PostgreSQL syntax
        is_sqlite = self.engine.url.get_backend_name() == 'sqlite'
        if is_sqlite:
            up_sql = self._convert_to_sqlite_syntax(up_sql)
            if down_sql:
                down_sql = self._convert_to_sqlite_syntax(down_sql)
        
        # Extract version and name from filename
        parts = filename.replace('.sql', '').split('_')
        version = parts[1]
        name = '_'.join(parts[2:])
        
        return self.apply_migration(version, name, up_sql, down_sql)
    
    def _convert_to_sqlite_syntax(self, sql_content):
        """Convert PostgreSQL syntax to SQLite-compatible syntax"""
        # Replace SERIAL with INTEGER PRIMARY KEY AUTOINCREMENT
        sql_content = sql_content.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT')
        
        # Remove IF NOT EXISTS from ALTER TABLE statements (SQLite doesn't support this)
        import re
        sql_content = re.sub(r'ALTER TABLE (\w+) ADD COLUMN IF NOT EXISTS', r'ALTER TABLE \1 ADD COLUMN', sql_content)
        
        # Remove ON CONFLICT DO NOTHING (SQLite uses different syntax)
        sql_content = sql_content.replace('ON CONFLICT DO NOTHING', '')
        
        # Remove ALTER COLUMN SET NOT NULL (SQLite doesn't support this)
        sql_content = re.sub(r'ALTER TABLE \w+ ALTER COLUMN \w+ SET NOT NULL;?', '', sql_content)
        
        # Remove DROP COLUMN IF EXISTS (SQLite doesn't support this)
        sql_content = re.sub(r'ALTER TABLE \w+ DROP COLUMN IF EXISTS \w+;?', '', sql_content)
        
        # Convert boolean defaults
        sql_content = sql_content.replace('BOOLEAN DEFAULT TRUE', 'BOOLEAN DEFAULT 1')
        sql_content = sql_content.replace('BOOLEAN DEFAULT FALSE', 'BOOLEAN DEFAULT 0')
        
        return sql_content
    
    def create_backup_before_migration(self):
        """Create a backup before running migrations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_before_migration_{timestamp}.sql"
        
        try:
            # Get database connection details
            import re
            m = re.match(r'postgresql://([^:]+):([^@]+)@([^:/]+)(?::(\d+))?/([^?]+)', self.database_url)
            if not m:
                print("❌ Could not parse database URL")
                return None
            
            db_user, db_pass, db_host, db_port, db_name = m.groups()
            db_port = db_port or '5432'
            
            # Run pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = db_pass
            
            subprocess.check_call([
                'pg_dump',
                '-h', db_host,
                '-p', db_port,
                '-U', db_user,
                '-F', 'plain',
                '-f', backup_file,
                db_name
            ], env=env)
            
            print(f"✅ Created backup: {backup_file}")
            return backup_file
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            return None
    
    def status(self):
        """Show migration status"""
        current_version = self.get_current_version()
        applied_migrations = self.get_applied_migrations()
        pending_migrations = self.get_pending_migrations()
        
        print("📊 Migration Status")
        print("=" * 50)
        print(f"Current Version: {current_version}")
        print(f"Applied Migrations: {len(applied_migrations)}")
        print(f"Pending Migrations: {len(pending_migrations)}")
        
        if applied_migrations:
            print("\n✅ Applied Migrations:")
            for migration in applied_migrations:
                print(f"   ├─ {migration['version']} - {migration['name']} ({migration['applied_at']})")
        
        if pending_migrations:
            print("\n⏳ Pending Migrations:")
            for filename in pending_migrations:
                version = self._extract_version(filename)
                name = '_'.join(filename.replace('.sql', '').split('_')[2:])
                print(f"   ├─ {version} - {name}")

def create_initial_migrations():
    """Create initial migration files for existing schema"""
    manager = MigrationManager()
    
    # Migration 1.0.0: Initial schema
    up_sql_1_0_0 = """
-- Create initial tables
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
"""
    
    down_sql_1_0_0 = """
-- Drop all tables
DROP TABLE IF EXISTS guest_reg_housekeeping CASCADE;
DROP TABLE IF EXISTS guest_reg_invoice_item CASCADE;
DROP TABLE IF EXISTS guest_reg_invoice CASCADE;
DROP TABLE IF EXISTS guest_reg_guest CASCADE;
DROP TABLE IF EXISTS guest_reg_registration CASCADE;
DROP TABLE IF EXISTS guest_reg_trip CASCADE;
DROP TABLE IF EXISTS guest_reg_user CASCADE;
"""
    
    # Migration 1.1.0: Add indexes for performance
    up_sql_1_1_0 = """
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
"""
    
    down_sql_1_1_0 = """
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
"""
    
    # Create migration files
    manager.create_migration("1.0.0", "initial_schema", up_sql_1_0_0, down_sql_1_0_0)
    manager.create_migration("1.1.0", "add_performance_indexes", up_sql_1_1_0, down_sql_1_1_0)
    
    print("✅ Created initial migration files")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrations.py [command]")
        print("Commands:")
        print("  status                    - Show migration status")
        print("  migrate [target_version]  - Run pending migrations")
        print("  rollback <version>        - Rollback specific migration")
        print("  create-initial            - Create initial migration files")
        print("  backup                    - Create backup before migration")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        manager = MigrationManager()
        manager.status()
    
    elif command == "migrate":
        target_version = sys.argv[2] if len(sys.argv) > 2 else None
        manager = MigrationManager()
        manager.migrate(target_version)
    
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("❌ Please specify version to rollback")
            sys.exit(1)
        version = sys.argv[2]
        manager = MigrationManager()
        manager.rollback_migration(version)
    
    elif command == "create-initial":
        create_initial_migrations()
    
    elif command == "backup":
        manager = MigrationManager()
        backup_file = manager.create_backup_before_migration()
        if backup_file:
            print(f"Backup created: {backup_file}")
    
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1) 