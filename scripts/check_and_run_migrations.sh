#!/bin/bash

# Migration Check and Run Script for Guest Registration System
# This script checks if the database is connected and runs migrations if needed

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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

# Configuration
MAX_RETRIES=30
RETRY_DELAY=2
PYTHON_SCRIPT="migrations.py"
MANAGE_SCRIPT="manage.py"

# Function to check if database is accessible
check_database_connection() {
    log "Checking database connection..."
    
    # Try to connect to database using Python
    python3 -c "
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

try:
    database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/airbnb_guests')
    engine = create_engine(database_url)
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database connection failed: {e}')
    sys.exit(1)
" 2>/dev/null
    
    return $?
}

# Function to check migration status
check_migration_status() {
    log "Checking migration status..."
    
    if [ -f "$MANAGE_SCRIPT" ]; then
        python3 "$MANAGE_SCRIPT" migrate status
        return $?
    elif [ -f "$PYTHON_SCRIPT" ]; then
        python3 "$PYTHON_SCRIPT" status
        return $?
    else
        error "No migration script found"
        return 1
    fi
}

# Function to run migrations
run_migrations() {
    log "Running migrations..."
    
    if [ -f "$MANAGE_SCRIPT" ]; then
        python3 "$MANAGE_SCRIPT" migrate
        return $?
    elif [ -f "$PYTHON_SCRIPT" ]; then
        python3 "$PYTHON_SCRIPT" migrate
        return $?
    else
        error "No migration script found"
        return 1
    fi
}

# Function to check if migrations are needed
check_if_migrations_needed() {
    log "Checking if migrations are needed..."
    
    # Run status check and capture output
    if [ -f "$MANAGE_SCRIPT" ]; then
        output=$(python3 "$MANAGE_SCRIPT" migrate status 2>&1)
    elif [ -f "$PYTHON_SCRIPT" ]; then
        output=$(python3 "$PYTHON_SCRIPT" status 2>&1)
    else
        error "No migration script found"
        return 1
    fi
    
    # Check if there are pending migrations
    if echo "$output" | grep -q "pending\|No pending migrations"; then
        if echo "$output" | grep -q "No pending migrations"; then
            success "No pending migrations found"
            return 0
        else
            warning "Pending migrations found"
            return 1
        fi
    else
        # If we can't determine, assume migrations might be needed
        warning "Could not determine migration status, proceeding with migration check"
        return 1
    fi
}

# Main execution
main() {
    log "Starting migration check and run process..."
    
    # Wait for database to be ready
    log "Waiting for database to be ready..."
    for i in $(seq 1 $MAX_RETRIES); do
        if check_database_connection; then
            success "Database is ready"
            break
        else
            if [ $i -eq $MAX_RETRIES ]; then
                error "Database connection failed after $MAX_RETRIES attempts"
                exit 1
            fi
            warning "Database not ready, retrying in ${RETRY_DELAY}s... (attempt $i/$MAX_RETRIES)"
            sleep $RETRY_DELAY
        fi
    done
    
    # Check if migrations are needed
    if check_if_migrations_needed; then
        success "Database is up to date, no migrations needed"
        exit 0
    fi
    
    # Run migrations
    log "Running migrations..."
    if run_migrations; then
        success "Migrations completed successfully"
        
        # Verify migration status after running
        log "Verifying migration status..."
        if check_migration_status; then
            success "Migration verification successful"
            exit 0
        else
            error "Migration verification failed"
            exit 1
        fi
    else
        error "Migrations failed"
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --check-only   Only check migration status, don't run migrations"
        echo "  --force        Force run migrations even if not needed"
        echo ""
        echo "This script checks database connectivity and runs migrations if needed."
        exit 0
        ;;
    --check-only)
        log "Check-only mode enabled"
        if check_database_connection; then
            success "Database is accessible"
            check_migration_status
        else
            error "Database is not accessible"
            exit 1
        fi
        exit 0
        ;;
    --force)
        log "Force mode enabled"
        if check_database_connection; then
            success "Database is accessible"
            run_migrations
        else
            error "Database is not accessible"
            exit 1
        fi
        exit 0
        ;;
    "")
        # No arguments, run normal flow
        main
        ;;
    *)
        error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 