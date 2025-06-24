#!/bin/bash

# Migration Check and Run Script for Guest Registration System
# This script checks if the database is connected and runs setup and migrations if needed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Initial debug logs
log "Script invoked: $0 $*"
log "Running as user: $(whoami), PID: $$"

# Dump selected critical environment variables
log "Dumping selected critical environment variables:"
log "POSTGRES_DB=${POSTGRES_DB:-<unset>}, POSTGRES_USER=${POSTGRES_USER:-<unset>}, POSTGRES_PASSWORD=${POSTGRES_PASSWORD:+***MASKED***}, DATABASE_URL=${DATABASE_URL:-<unset>}, TABLE_PREFIX=${TABLE_PREFIX:-<unset>}"
log "SECRET_KEY=${SECRET_KEY:+***MASKED***}, MAIL_SERVER=${MAIL_SERVER:-<unset>}, MAIL_PORT=${MAIL_PORT:-<unset>}, MAIL_USE_TLS=${MAIL_USE_TLS:-<unset>}, MAIL_USERNAME=${MAIL_USERNAME:-<unset>}, MAIL_PASSWORD=${MAIL_PASSWORD:+***MASKED***}"
log "UPLOAD_FOLDER=${UPLOAD_FOLDER:-<unset>}, MAX_CONTENT_LENGTH=${MAX_CONTENT_LENGTH:-<unset>}"
# Full environment dump (for deeper debugging)
env | while IFS= read -r line; do log "$line"; done

# Configuration
MAX_RETRIES=30
RETRY_DELAY=2
PYTHON_SCRIPT="migrations.py"
MANAGE_SCRIPT="manage.py"
SETUP_SCRIPT="setup.py"

log "Configurations: MAX_RETRIES=$MAX_RETRIES, RETRY_DELAY=$RETRY_DELAY, PYTHON_SCRIPT=$PYTHON_SCRIPT, MANAGE_SCRIPT=$MANAGE_SCRIPT, SETUP_SCRIPT=$SETUP_SCRIPT, TABLE_PREFIX=${TABLE_PREFIX:-guest_reg_}"

# Function to check database connectivity
check_database_connection() {
    log "--> Enter check_database_connection()"
    log "Executing Python DB connection test"
    local output status
    output=$(python3 - << 'PYCODE'
import os, sys
print(f'Python version: {sys.version}')
print(f'Python executable: {sys.executable}')

# Check if psycopg2 is available
try:
    import psycopg2
    print(f'psycopg2 version: {psycopg2.__version__}')
    print(f'psycopg2 path: {psycopg2.__file__}')
except ImportError as e:
    print(f'psycopg2 import error: {e}')
    print('Attempting to install psycopg2-binary...')
    import subprocess
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary>=2.9.5'])
        import psycopg2
        print(f'psycopg2 successfully installed, version: {psycopg2.__version__}')
    except Exception as install_error:
        print(f'Failed to install psycopg2: {install_error}')
        sys.exit(1)

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
print(f'DATABASE_URL={url}')
try:
    engine = create_engine(url)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
PYCODE
) 2>&1
    status=$?
    log "Python DB test output: $output"
    if [ $status -eq 0 ]; then success "DB connection test passed"; else error "DB connection test failed"; fi
    log "<-- Exit check_database_connection(), status=$status"
    return $status
}

# Function to check if database is empty
check_database_empty() {
    log "--> Enter check_database_empty()"
    log "Executing Python DB empty check"
    local output status
    output=$(python3 - << 'PYCODE'
import os, sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
load_dotenv()
url = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
print(f'DATABASE_URL={url}')
inspector = inspect(create_engine(url))
tables = inspector.get_table_names()
prefix = os.getenv('TABLE_PREFIX', 'guest_reg_')
print(f'TABLE_PREFIX={prefix}')
app = [t for t in tables if t.startswith(prefix)]
if not app:
    print('Database is empty (no application tables found)')
    sys.exit(0)
else:
    print(f'Database has {len(app)} application tables: {app}')
    sys.exit(1)
PYCODE
) 2>&1
    status=$?
    log "Python DB empty check output: $output"
    if [ $status -eq 0 ]; then warning "Database empty"; else success "Database has tables"; fi
    log "<-- Exit check_database_empty(), status=$status"
    return $status
}

# Function to check migration status
check_migration_status() {
    log "--> Enter check_migration_status()"
    local output status
    if [ -f "$MANAGE_SCRIPT" ]; then
        log "Using $MANAGE_SCRIPT"
        output=$(python3 "$MANAGE_SCRIPT" migrate status 2>&1)
    else
        log "Using $PYTHON_SCRIPT"
        output=$(python3 "$PYTHON_SCRIPT" status 2>&1)
    fi
    status=$?
    log "Migration status output: $output"
    log "<-- Exit check_migration_status(), status=$status"
    return $status
}

# Function to run migrations
run_migrations() {
    log "--> Enter run_migrations()"
    if [ -f "$MANAGE_SCRIPT" ]; then
        log "Command: python3 $MANAGE_SCRIPT migrate"
        python3 "$MANAGE_SCRIPT" migrate
    else
        log "Command: python3 $PYTHON_SCRIPT migrate"
        python3 "$PYTHON_SCRIPT" migrate
    fi
    local status=$?
    if [ $status -eq 0 ]; then success "Migrations successful"; else error "Migrations failed"; fi
    log "<-- Exit run_migrations(), status=$status"
    return $status
}

# Function to run setup
run_setup() {
    log "--> Enter run_setup()"
    
    # Check for Docker setup script first
    if [ -f "setup_docker.py" ] && [ "$DOCKER_ENV" = "true" ]; then
        log "Using Docker setup script: setup_docker.py"
        python3 setup_docker.py
        local status=$?
        if [ $status -eq 0 ]; then success "Docker setup completed"; else error "Docker setup failed"; fi
        log "<-- Exit run_setup(), status=$status"
        return $status
    fi
    
    # Fallback to regular setup script
    if [ -f "$SETUP_SCRIPT" ]; then
        # In Docker, always use non-interactive setup
        if [ -t 0 ] && [ "$DOCKER_ENV" != "true" ]; then
            log "Interactive setup: python3 $SETUP_SCRIPT"
            python3 "$SETUP_SCRIPT"
        else
            log "Non-interactive setup: default admin creation"
            python3 - << 'PYCODE'
import os, sys
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
load_dotenv()

try:
    from app import app, db, User
    print("✅ App modules imported successfully")
except Exception as e:
    print(f"❌ Error importing app modules: {e}")
    sys.exit(1)

try:
    with app.app_context():
        print("✅ App context created")
        
        # Check if admin already exists (not deleted)
        existing_admin = User.query.filter_by(is_deleted=False).first()
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin.username}")
            sys.exit(0)
        
        print("Creating default admin user...")
        admin = User(
            username='admin', 
            email='admin@example.com', 
            password_hash=generate_password_hash('admin123'), 
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Default admin created successfully')
        print('   Username: admin')
        print('   Password: admin123')
        print('   Email: admin@example.com')
        sys.exit(0)
except Exception as e:
    print(f"❌ Error creating admin user: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYCODE
        fi
    else
        error "Setup script not found: $SETUP_SCRIPT"
        log "Current directory: $(pwd)"
        log "Files in current directory: $(ls -la)"
        return 1
    fi
    local status=$?
    if [ $status -eq 0 ]; then success "Setup completed"; else error "Setup errors"; fi
    log "<-- Exit run_setup(), status=$status"
    return $status
}

# Function to check if migrations are needed
check_if_migrations_needed() {
    log "--> Enter check_if_migrations_needed()"
    local output status
    if [ -f "$MANAGE_SCRIPT" ]; then output=$(python3 "$MANAGE_SCRIPT" migrate status 2>&1); else output=$(python3 "$PYTHON_SCRIPT" status 2>&1); fi
    log "Raw migration status: $output"
    if echo "$output" | grep -q "No pending migrations"; then success "No pending migrations"; return 0; elif echo "$output" | grep -q "pending"; then warning "Pending migrations"; return 1; else warning "Unknown status, assume pending"; return 1; fi
}

# Function to check if setup is needed
check_if_setup_needed() {
    log "--> Enter check_if_setup_needed()"
    if check_database_empty; then warning "Setup needed"; return 0; else success "Setup not needed"; return 1; fi
}

# Main
main() {
    log "--> Enter main()"
    log "Waiting for database readiness"
    for i in $(seq 1 $MAX_RETRIES); do
        log "DB connection attempt $i"
        if check_database_connection; then success "DB ready after $i attempts"; break; fi
        if [ $i -eq $MAX_RETRIES ]; then error "DB unreachable after $MAX_RETRIES attempts"; exit 1; fi
        sleep $RETRY_DELAY
    done

    if check_if_setup_needed; then log "Running setup"; run_setup || warning "Setup failed"; fi
    if check_if_migrations_needed; then success "DB up to date"; exit 0; fi

    log "Initiating migrations"
    run_migrations || { error "Migration run failed"; exit 1; }
    log "Verifying migrations"
    check_migration_status && success "Migration verification passed" || { error "Migration verification failed"; exit 1; }
    log "<-- Exit main()"
}

# Argument handling
log "Parsing arguments: $*"
case "${1:-}" in
    --help|-h)
        log "Help requested"
        echo "Usage: $0 [OPTIONS]"; echo; echo "Options:"; echo "  --help, -h     Show help"; echo "  --check-only   Only check status"; echo "  --force        Force migrations"; echo "  --setup-only   Only setup"; echo "  --migrate-only Only migrate"
        exit 0;;
    --check-only)
        log "Mode: check-only"
        check_database_connection && success "DB accessible" && check_migration_status || exit 1
        exit 0;;
    --force)
        log "Mode: force"
        check_database_connection && run_migrations || exit 1
        exit 0;;
    --setup-only)
        log "Mode: setup-only"
        check_database_connection && run_setup || exit 1
        exit 0;;
    --migrate-only)
        log "Mode: migrate-only"
        check_database_connection && run_migrations || exit 1
        exit 0;;
    "")
        main;;
    *)
        error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1;;
esac
