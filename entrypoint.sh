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

# Start the Flask application
log "Starting Flask application..."
if [ -f "app.py" ]; then
    exec python app.py
else
    error "app.py not found!"
    exit 1
fi