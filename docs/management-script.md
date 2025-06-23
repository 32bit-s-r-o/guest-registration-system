# Universal Management Script Documentation

[← Back to Documentation Index](../docs/README.md)

## Overview

The `manage.py` script is a comprehensive management tool for the Guest Registration System that provides unified access to all system operations including tests, migrations, seeds, backups, and utilities.

## Quick Start

```bash
# Show all available commands
python manage.py --help

# Check system status
python manage.py status

# Run all tests
python manage.py test

# Run migrations
python manage.py migrate migrate

# Setup system from scratch
python manage.py setup
```

## Available Commands

### 1. Test Operations (`test`)

Runs all available test scripts in the system.

```bash
# Run all tests
python manage.py test

# Run tests with specific arguments
python manage.py test --verbose
```

**Available Test Scripts:**
- `test_backup_api.py` - Backup API functionality tests
- `test_backup_functionality.py` - Backup system tests
- `test_migration_system.py` - Migration system tests
- `system_test.py` - Comprehensive system tests
- `test_email_functionality.py` - Email functionality tests
- `test_csv_export.py` - CSV export tests
- `test_language_picker.py` - Language picker tests

### 2. Migration Operations (`migrate`)

Manages database migrations using the migration system.

```bash
# Check migration status
python manage.py migrate status

# Apply pending migrations
python manage.py migrate migrate

# Rollback last migration
python manage.py migrate rollback

# Show migration history
python manage.py migrate history
```

**Related Documentation:** [Database Migrations](migrations.md)

### 3. Seed Operations (`seed`)

Runs seed data scripts to populate the database with sample data.

```bash
# Run all seed operations
python manage.py seed

# Run specific seed with arguments
python manage.py seed --force
```

**Available Seed Scripts:**
- `create_test_registration.py` - Creates test guest registrations
- `create_housekeeper_data.py` - Creates housekeeper sample data

### 4. Backup Operations (`backup`)

Runs backup functionality tests and operations.

```bash
# Run backup tests
python manage.py backup

# Run backup with specific parameters
python manage.py backup --full
```

**Related Documentation:** [Backup System](backup-system.md)

### 5. Utility Operations (`utility`)

Lists and runs utility scripts for system maintenance.

```bash
# List available utilities
python manage.py utility

# Run all utilities
python manage.py utility --all
```

**Available Utility Scripts:**
- `extract_translations.py` - Extract translation strings
- `add_missing_czech_translations.py` - Add missing Czech translations
- `fix_fuzzy_translations.py` - Fix fuzzy translation matches
- `fix_user_sequence.py` - Fix user ID sequences
- `migrate_age_language_photo.py` - Migrate age/language/photo data
- `migrate_confirm_code.py` - Migrate confirmation codes
- `migrate_to_user_role_system.py` - Migrate to user role system
- `quick_reset.py` - Quick system reset
- `reset_data.py` - Reset system data
- `setup.py` - System setup

### 6. Status Operations (`status`)

Shows comprehensive system status information.

```bash
# Show system status
python manage.py status
```

**Status Information:**
- Flask application running status
- Database version and connection
- Migration status (applied/pending)
- Available script categories and counts

### 7. Cleanup Operations (`clean`)

Cleans up temporary files, caches, and backup files.

```bash
# Clean up system
python manage.py clean
```

**Cleanup Items:**
- `*.pyc` files (Python bytecode)
- `__pycache__` directories
- `*.log` files
- `*.tmp` files
- `backup_*.sql` files
- `backup_*.sql.gz` files

### 8. Setup Operations (`setup`)

Sets up the system from scratch with all necessary components.

```bash
# Setup complete system
python manage.py setup
```

**Setup Steps:**
1. Create necessary directories
2. Run database migrations
3. Create seed data
4. Run system tests
5. Create initial backup

### 9. All Operations (`all`)

Runs all operations in sequence for comprehensive system management.

```bash
# Run all operations
python manage.py all
```

**All Operations Sequence:**
1. Status check
2. Cleanup
3. Migrations
4. Seeds
5. Tests
6. Backups

### 10. Flask App Parameters

The Flask application (`app.py`) supports various command-line parameters for flexible deployment:

```bash
# Basic parameters
--host HOST           # Host to bind to (default: 127.0.0.1)
--port PORT           # Port to bind to (default: 5000)

# Debug and development
--debug               # Enable debug mode
--no-debug            # Disable debug mode
--reload              # Enable auto-reload on code changes

# Production features
--threaded            # Enable threading for concurrent requests
--ssl-context SSL     # SSL context for HTTPS (e.g., "adhoc" for self-signed)
```

**Common Usage Examples:**
```bash
# Development with auto-reload
python app.py --debug --reload --port 5001

# Production server (accessible from network)
python app.py --host 0.0.0.0 --port 80 --no-debug --threaded

# HTTPS with self-signed certificate
python app.py --ssl-context adhoc --port 443

# Custom port for testing
python app.py --port 8080
```

**Parameter Testing:**
```bash
# Test parameter functionality
python test_app_parameters.py
```

This test script verifies that the app starts correctly with various parameter combinations.

## Advanced Usage

### Command Chaining

You can chain commands by running multiple operations:

```bash
# Clean, migrate, and test
python manage.py clean && python manage.py migrate migrate && python manage.py test
```

### Script Arguments

Most commands accept additional arguments that are passed to the underlying scripts:

```bash
# Run migrations with verbose output
python manage.py migrate migrate --verbose

# Run tests with specific test file
python manage.py test test_backup_api.py
```

### Error Handling

The management script provides comprehensive error handling:

- **Timeout Protection**: Scripts timeout after 5 minutes
- **Error Logging**: All errors are logged with timestamps
- **Graceful Failure**: Failed operations don't stop the entire process
- **Status Reporting**: Detailed success/failure reporting

## System Requirements

### Prerequisites

- Python 3.7+
- PostgreSQL database
- Required Python packages (see `requirements.txt`)

### Directory Structure

The script expects the following directory structure:

```
airbnb/
├── manage.py                 # This management script
├── app.py                   # Main Flask application
├── migrations.py            # Migration system
├── migrations/              # Migration files
├── tests/                   # Test scripts
├── uploads/                 # Upload directory
├── static/                  # Static files
└── templates/               # Template files
```

## Best Practices

### 1. Regular Maintenance

```bash
# Weekly maintenance routine
python manage.py clean
python manage.py status
python manage.py test
```

### 2. Before Deployments

```bash
# Pre-deployment checklist
python manage.py status
python manage.py migrate status
python manage.py test
python manage.py backup
```

### 3. After Updates

```bash
# Post-update routine
python manage.py migrate migrate
python manage.py test
python manage.py status
```

### 4. Troubleshooting

```bash
# Diagnostic sequence
python manage.py status
python manage.py clean
python manage.py migrate status
python manage.py test
```

## Configuration

### Environment Variables

The management script respects the same environment variables as the main application:

- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - Application secret key
- `FLASK_ENV` - Flask environment

### Custom Scripts

To add custom scripts to the management system:

1. Add the script to the appropriate category in `manage.py`
2. Ensure the script has proper error handling
3. Test the script integration

## Troubleshooting

### Common Issues

1. **Script Not Found**: Ensure all referenced scripts exist in the project directory
2. **Permission Errors**: Check file permissions for script execution
3. **Database Connection**: Verify database configuration and connectivity
4. **Timeout Errors**: Increase timeout values for long-running operations

### Debug Mode

For debugging, you can run individual scripts directly:

```bash
# Debug specific script
python migrations.py status

# Debug with verbose output
python -v manage.py status
```

## Integration

### CI/CD Integration

The management script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run System Tests
  run: python manage.py test

- name: Run Migrations
  run: python manage.py migrate migrate

- name: Check Status
  run: python manage.py status
```

### Monitoring Integration

Use the status command for monitoring:

```bash
# Health check
python manage.py status | grep -q "SUCCESS" && echo "System OK" || echo "System Issues"
```

## Current System Status

- **Database Version**: 000001 (Latest)
- **Applied Migrations**: 2
- **Pending Migrations**: 0
- **Flask Application**: ✅ Running
- **All Tests**: ✅ Passing (9/9)
- **Management Script**: ✅ Fully Functional

## Related Documentation

- [Database Migrations](migrations.md) - Migration system details
- [Backup System](backup-system.md) - Backup functionality
- [Testing Guide](testing.md) - Comprehensive testing
- [Installation Guide](installation.md) - System setup

## Support

For issues with the management script:

1. Check the status command output
2. Review error logs
3. Run individual scripts for isolation
4. Check system requirements and configuration

## Version History

- **v1.0.0**: Initial release with basic command structure
- **v1.1.0**: Added comprehensive error handling and logging
- **v1.2.0**: Added setup and all operations commands
- **v1.3.0**: Enhanced status reporting and cleanup operations

---

[← Back to Documentation Index](../docs/README.md) 