# Migration System Documentation

## Overview

The Guest Registration System now includes a comprehensive versioning and migration system that allows you to:

- **Track database schema changes** with version control
- **Apply migrations safely** with rollback capabilities
- **Manage application versions** and compatibility
- **Automate database updates** with backup protection
- **Test migrations** before applying to production

## System Components

### 1. Version Management (`version.py`)
- Tracks application and database versions
- Manages upgrade paths and compatibility
- Provides changelog and version history
- Handles version comparison and validation

### 2. Migration Management (`migrations.py`)
- Creates and applies database migrations
- Tracks applied migrations in database
- Provides rollback functionality
- Validates migration integrity with checksums

### 3. Migration Files (`migrations/`)
- SQL files with up/down migration scripts
- Versioned naming convention: `timestamp_version_name.sql`
- Includes rollback scripts for safe operations

## Current Versions

- **Application Version**: 1.0.0
- **Database Schema**: 1.1.0 (with performance indexes)
- **Minimum Required DB Version**: 1.0.0

## Migration Files

### 1.0.0 - Initial Schema
- Creates all core tables (users, trips, registrations, guests, invoices, housekeeping)
- Establishes foreign key relationships
- Sets up basic constraints and defaults

### 1.1.0 - Performance Indexes
- Adds database indexes for improved query performance
- Covers frequently queried columns
- Optimizes joins and filtering operations

## Usage

### Command Line Interface

#### Check Migration Status
```bash
python migrations.py status
```

#### Run Pending Migrations
```bash
# Run all pending migrations
python migrations.py migrate

# Run migrations up to specific version
python migrations.py migrate 1.2.0
```

#### Rollback Migration
```bash
python migrations.py rollback 1.1.0
```

#### Create Backup
```bash
python migrations.py backup
```

#### Version Information
```bash
python version.py current
python version.py info
python version.py changelog 1.1.0
python version.py compatibility 1.0.0
```

### Web Interface

#### Migration Management Page
- Access: `/admin/migrations`
- View current version and pending migrations
- Run migrations with one-click
- Rollback specific migrations
- Check version compatibility

#### Version API Endpoints
- `GET /api/version` - Get version information
- `GET /api/version/compatibility` - Check compatibility
- `GET /api/version/changelog/<version>` - Get changelog

## Migration Workflow

### 1. Development Workflow

```bash
# 1. Create new migration
python migrations.py create-migration 1.2.0 add_new_feature

# 2. Edit migration file in migrations/
# 3. Test migration locally
python migrations.py migrate

# 4. Test rollback
python migrations.py rollback 1.2.0

# 5. Commit migration files to version control
```

### 2. Production Deployment

```bash
# 1. Create backup before migration
python migrations.py backup

# 2. Run migrations
python migrations.py migrate

# 3. Verify application works
# 4. Monitor logs for any issues
```

### 3. Emergency Rollback

```bash
# 1. Stop application
# 2. Rollback problematic migration
python migrations.py rollback 1.2.0

# 3. Restart application
# 4. Investigate and fix issues
```

## Creating New Migrations

### Migration File Structure

```sql
-- Migration: 1.2.0 - add_new_table
-- Created: 2025-01-15T10:30:00
-- Up Migration
CREATE TABLE guest_reg_new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Down Migration (Rollback)
DROP TABLE guest_reg_new_table;
```

### Migration Naming Convention

- **Format**: `YYYYMMDD_HHMMSS_VERSION_NAME.sql`
- **Example**: `20250115_103000_1.2.0_add_new_table.sql`
- **Version**: Semantic versioning (major.minor.patch)
- **Name**: Descriptive name with underscores

### Best Practices

1. **Always include rollback scripts**
2. **Test migrations in development first**
3. **Use IF NOT EXISTS for table creation**
4. **Use CASCADE for table drops in rollback**
5. **Add indexes for performance**
6. **Document breaking changes**

## Version Management

### Version Compatibility

The system tracks compatibility between:
- Application version
- Database schema version
- Minimum required database version

### Upgrade Paths

```python
upgrade_paths = {
    "1.0.0": ["1.1.0", "1.2.0"],
    "1.1.0": ["1.2.0"],
    "1.2.0": ["1.3.0"],
}
```

### Version History

Each version includes:
- Release date
- Feature list
- Database schema version
- Breaking changes
- Upgrade notes

## Testing

### Run Migration Tests
```bash
python test_migration_system.py
```

### Test Coverage
- Migration file validation
- Version system functionality
- Command line interface
- Web interface integration

## Safety Features

### 1. Automatic Backups
- Creates backup before each migration
- Uses `pg_dump` for complete database backup
- Stores backup with timestamp

### 2. Checksum Validation
- Calculates SHA256 checksum of migration content
- Prevents tampering with migration files
- Validates migration integrity

### 3. Transaction Safety
- Migrations run in database transactions
- Automatic rollback on failure
- No partial migrations

### 4. Version Locking
- Prevents incompatible version combinations
- Validates upgrade paths
- Warns about breaking changes

## Troubleshooting

### Common Issues

#### Migration Fails
```bash
# Check migration status
python migrations.py status

# Check database logs
tail -f /var/log/postgresql/postgresql-*.log

# Rollback and retry
python migrations.py rollback <version>
```

#### Version Compatibility Error
```bash
# Check current versions
python version.py info

# Check compatibility
python version.py compatibility <db_version>

# Update database version
python migrations.py migrate
```

#### Missing Migration Files
```bash
# Recreate migration files
python migrations.py create-initial

# Check file permissions
ls -la migrations/
```

### Recovery Procedures

#### Database Corruption
1. Stop application
2. Restore from latest backup
3. Re-run migrations from backup point
4. Verify data integrity

#### Migration Rollback Failure
1. Check migration logs
2. Manually fix database state
3. Update migration tracking table
4. Test application functionality

## Monitoring

### Migration Logs
- Check application logs for migration events
- Monitor database logs for SQL errors
- Track migration execution times

### Health Checks
- Version compatibility status
- Pending migration count
- Backup file existence and size
- Migration table integrity

## Future Enhancements

### Planned Features
- **Migration Dependencies**: Handle complex migration chains
- **Data Migrations**: Support for data transformation
- **Migration Testing**: Automated migration validation
- **Rollback Scheduling**: Planned rollback windows
- **Migration Analytics**: Performance and usage metrics

### Version Roadmap
- **1.2.0**: Multi-language support enhancements
- **1.3.0**: Advanced reporting features
- **2.0.0**: Major architecture improvements

## Support

For migration system issues:
1. Check this documentation
2. Review migration logs
3. Test in development environment
4. Create backup before troubleshooting
5. Contact system administrator

---

**Last Updated**: 2025-01-15
**System Version**: 1.1.0
**Documentation Version**: 1.0.0 