# Database Migration System Documentation

[← Back to Documentation Index](../docs/README.md)

## Overview

The Guest Registration System includes a comprehensive database migration system that handles versioning, migrations, and rollbacks. This system ensures database schema changes are tracked, versioned, and can be safely applied or rolled back.

## Quick Start

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

## Current System Status

- **Database Version**: 000001 (Latest)
- **Applied Migrations**: 2
- **Pending Migrations**: 0
- **Migration System**: ✅ Fully Functional

## Migration System Architecture

### Core Components

1. **MigrationManager Class** - Main migration orchestration
2. **Migration Files** - SQL files in `migrations/` directory
3. **Version Tracking** - Database table for tracking applied migrations
4. **Rollback Support** - Ability to reverse migrations

### Database Schema

The migration system uses a dedicated table to track applied migrations:

```sql
CREATE TABLE guest_reg_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64),
    rollback_sql TEXT
);
```

## Migration Commands

### Status Check

```bash
python manage.py migrate status
```

Shows:
- Current database version
- Applied migrations list
- Pending migrations list
- Version compatibility status

### Apply Migrations

```bash
python manage.py migrate migrate
```

Features:
- Automatic backup before migration
- Transaction-based execution
- Error handling and rollback
- Progress reporting

### Rollback Migrations

```bash
python manage.py migrate rollback <version>
```

Features:
- Safe rollback with backup
- Dependency checking
- Transaction safety

### Migration History

```bash
python manage.py migrate history
```

Shows:
- Complete migration timeline
- Applied dates
- Checksums for verification

## Migration File Structure

### File Naming Convention

```
YYYYMMDD_HHMMSS_version_name.sql
```

Example: `20250101_000000_1.0.0_initial_schema.sql`

### File Content Structure

```sql
-- Migration: 1.0.0 - initial_schema
-- Created: 2025-01-01T00:00:00
-- Up Migration
CREATE TABLE guest_reg_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(120) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Down Migration (Rollback)
DROP TABLE IF EXISTS guest_reg_user;
```

## Available Migrations

### Applied Migrations

1. **000000 - 1.0.0_initial_schema**
   - Creates initial database schema
   - User, Trip, Registration, Guest tables
   - Basic indexes and constraints

2. **000001 - 1.1.0_add_performance_indexes**
   - Adds performance optimization indexes
   - Improves query performance
   - Foreign key optimizations

### Pending Migrations

Currently no pending migrations.

## Migration Management

### Creating New Migrations

```bash
# Using the migration manager
python migrations.py create 1.2.0 add_new_feature
```

### Manual Migration Creation

1. Create SQL file in `migrations/` directory
2. Follow naming convention
3. Include up and down migrations
4. Test thoroughly

### Migration Testing

```bash
# Test migration system
python test_migration_system.py

# Test individual migrations
python migrations.py test <migration_file>
```

## Safety Features

### Automatic Backups

- Backup created before each migration
- Backup stored with timestamp
- Automatic cleanup of old backups

### Transaction Safety

- All migrations run in transactions
- Automatic rollback on failure
- Checksum verification

### Dependency Management

- Migration dependency tracking
- Order enforcement
- Conflict detection

## Integration with Management Script

The migration system is fully integrated with the universal management script:

```bash
# Check status
python manage.py status

# Run migrations
python manage.py migrate migrate

# Setup system
python manage.py setup
```

## Web Interface

### Admin Migration Page

Access via: `/admin/migrations`

Features:
- Visual migration status
- One-click migration execution
- Rollback functionality
- Version compatibility checking

### API Endpoints

- `GET /api/version` - Get current version
- `GET /api/version/compatibility` - Check compatibility
- `GET /api/version/changelog/<version>` - Get changelog

## Best Practices

### Before Migrations

1. **Backup Database**
   ```bash
   python manage.py backup
   ```

2. **Check Status**
   ```bash
   python manage.py migrate status
   ```

3. **Test in Development**
   ```bash
   python test_migration_system.py
   ```

### During Migrations

1. **Monitor Progress**
   - Watch for error messages
   - Check migration logs
   - Verify database state

2. **Handle Errors**
   - Review error details
   - Check migration file syntax
   - Verify database connectivity

### After Migrations

1. **Verify Success**
   ```bash
   python manage.py status
   ```

2. **Test Application**
   ```bash
   python manage.py test
   ```

3. **Update Documentation**
   - Update migration history
   - Document schema changes
   - Update API documentation

## Troubleshooting

### Common Issues

1. **Migration Fails**
   - Check SQL syntax
   - Verify database permissions
   - Review error logs

2. **Version Conflicts**
   - Check applied migrations
   - Verify migration order
   - Resolve conflicts manually

3. **Rollback Issues**
   - Check rollback SQL
   - Verify dependencies
   - Use manual rollback if needed

### Debug Commands

```bash
# Verbose migration output
python migrations.py migrate --verbose

# Test specific migration
python migrations.py test <migration_file>

# Check migration file syntax
python migrations.py validate <migration_file>
```

## Version Compatibility

### Version Matrix

| App Version | Database Version | Status |
|-------------|------------------|---------|
| 1.0.0       | 000000           | ✅ Compatible |
| 1.0.0       | 000001           | ✅ Compatible |
| 1.1.0       | 000001           | ✅ Compatible |

### Compatibility Checking

```bash
# Check compatibility
python manage.py status

# API compatibility check
curl http://localhost:5000/api/version/compatibility
```

## Related Documentation

- [Universal Management Script](management-script.md) - Management commands
- [Backup System](backup-system.md) - Backup and restore
- [Testing Guide](testing.md) - Migration testing
- [Installation Guide](installation.md) - System setup

## Support

For migration issues:

1. Check migration status
2. Review error logs
3. Test migrations in development
4. Create backup before manual fixes

## Version History

- **v1.0.0**: Initial migration system
- **v1.1.0**: Added performance indexes
- **v1.2.0**: Enhanced rollback support
- **v1.3.0**: Web interface integration

---

[← Back to Documentation Index](../docs/README.md) 