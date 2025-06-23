#!/bin/bash

# Simple wrapper script to run migrations
# This script can be used both inside and outside Docker

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATION_SCRIPT="$SCRIPT_DIR/scripts/check_and_run_migrations.sh"

if [ -f "$MIGRATION_SCRIPT" ]; then
    echo "Running migration script: $MIGRATION_SCRIPT"
    exec "$MIGRATION_SCRIPT" "$@"
else
    echo "Error: Migration script not found at $MIGRATION_SCRIPT"
    exit 1
fi 