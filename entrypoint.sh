#!/bin/bash

# Entrypoint script for Guest Registration System
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

log "Starting Guest Registration System..."

# Ensure cache directories exist and have proper permissions
log "Setting up cache directories..."
mkdir -p ~/.cache/pip ~/.cache/fontconfig
chmod 755 ~/.cache ~/.cache/pip ~/.cache/fontconfig 2>/dev/null || true

# Quick verification that core modules are still working
log "Quick module verification..."
python -c "
import PIL
from PIL import _imaging
import cffi
import weasyprint
print('All critical modules available')
" || {
    error "Critical modules not working - container build issue"
    exit 1
}

success "All dependencies verified"

# Run database setup and migrations
log "Running database setup and migrations..."
if [ -f "scripts/check_and_run_migrations.sh" ]; then
    chmod +x scripts/check_and_run_migrations.sh
    ./scripts/check_and_run_migrations.sh
else
    error "Migration script not found!"
    exit 1
fi

success "Database setup completed"

# Determine server configuration
FLASK_ENV=${FLASK_ENV:-production}
GUNICORN_WORKERS=${GUNICORN_WORKERS:-4}
GUNICORN_WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-120}
GUNICORN_KEEP_ALIVE=${GUNICORN_KEEP_ALIVE:-2}
GUNICORN_MAX_REQUESTS=${GUNICORN_MAX_REQUESTS:-1000}
GUNICORN_MAX_REQUESTS_JITTER=${GUNICORN_MAX_REQUESTS_JITTER:-100}
APP_PORT=${APP_PORT:-5000}

# Start the application with appropriate server
if [ "$FLASK_ENV" = "production" ]; then
    log "Starting production server with Gunicorn..."
    
    # Check if Gunicorn is available
    if command -v gunicorn >/dev/null 2>&1; then
        log "Gunicorn configuration:"
        log "  Workers: $GUNICORN_WORKERS"
        log "  Worker Class: $GUNICORN_WORKER_CLASS"
        log "  Timeout: $GUNICORN_TIMEOUT"
        log "  Max Requests: $GUNICORN_MAX_REQUESTS"
        log "  Port: $APP_PORT"
        
        # Use configuration file if available, otherwise use command line arguments
        if [ -f "gunicorn.conf.py" ]; then
            log "Using gunicorn.conf.py configuration file"
            exec gunicorn -c gunicorn.conf.py app:app
        else
            log "Using command line configuration"
            exec gunicorn \
                --bind "0.0.0.0:$APP_PORT" \
                --workers "$GUNICORN_WORKERS" \
                --worker-class "$GUNICORN_WORKER_CLASS" \
                --timeout "$GUNICORN_TIMEOUT" \
                --keep-alive "$GUNICORN_KEEP_ALIVE" \
                --max-requests "$GUNICORN_MAX_REQUESTS" \
                --max-requests-jitter "$GUNICORN_MAX_REQUESTS_JITTER" \
                --access-logfile - \
                --error-logfile - \
                --log-level info \
                --preload \
                app:app
        fi
    else
        warning "Gunicorn not found, falling back to Flask development server"
        log "Starting Flask development server..."
        exec python app.py --host 0.0.0.0 --port "$APP_PORT" --no-debug --threaded
    fi
else
    log "Starting development server with Flask..."
    exec python app.py --host 0.0.0.0 --port "$APP_PORT" --debug --reload
fi