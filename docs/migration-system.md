# Migration System Documentation

## Overview

The Guest Registration System includes an automated migration system that ensures the database schema is always up to date. The system consists of:

1. **Migration Script**: `scripts/check_and_run_migrations.sh` - Main migration orchestration script
2. **Wrapper Script**: `run_migrations.sh` - Simple wrapper for easy access
3. **Docker Integration**: Automatic migration execution in Docker containers
4. **Python Migration System**: `migrations.py` - Core migration logic

## How It Works

### Automatic Migration in Docker

When running the application with Docker Compose, migrations are automatically handled:

1. **Migration Service**: A dedicated service runs migrations before the main app starts
2. **Database Health Check**: The system waits for the database to be healthy
3. **Migration Execution**: Pending migrations are automatically applied
4. **Verification**: Migration status is verified after execution

### Manual Migration Execution

You can run migrations manually using the provided scripts:

```bash
# Run migrations with automatic checks
./run_migrations.sh

# Check migration status only
./run_migrations.sh --check-only

# Force run migrations
./run_migrations.sh --force

# Get help
./run_migrations.sh --help
```

## Migration Script Features

### Database Connectivity Check

The script automatically:
- Waits for the database to be ready (up to 30 retries with 2-second intervals)
- Tests database connectivity using SQLAlchemy
- Provides clear error messages if connection fails

### Migration Status Detection

The script intelligently detects:
- Whether migrations are needed
- Current database version
- Pending migrations
- Migration history

### Safe Migration Execution

Migrations are executed safely with:
- Error handling and rollback capabilities
- Verification after execution
- Detailed logging with colored output
- Non-blocking execution (continues even if migrations fail)

## Docker Integration

### Docker Compose Setup

The `docker-compose.yml` includes:

```yaml
# Migration Service (runs once and exits)
migrations:
  build:
    context: .
    dockerfile: Dockerfile
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  command: ["/app/scripts/check_and_run_migrations.sh"]
  restart: "no"

# Main Application
app:
  depends_on:
    migrations:
      condition: service_completed_successfully
    # ... other dependencies
```

### Dockerfile Integration

The Dockerfile includes an entrypoint script that:
1. Runs migration checks before starting the application
2. Continues even if migrations fail (for development)
3. Provides clear logging of the migration process

## Usage Examples

### Development Environment

```bash
# Start the entire stack with automatic migrations
docker-compose up

# Run migrations manually
docker-compose run --rm app /app/scripts/check_and_run_migrations.sh

# Check migration status
docker-compose run --rm app /app/scripts/check_and_run_migrations.sh --check-only
```

### Production Environment

```bash
# Deploy with automatic migrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run migrations manually in production
docker-compose exec app /app/scripts/check_and_run_migrations.sh
```

### Local Development

```bash
# Run migrations locally (requires database connection)
./run_migrations.sh

# Check status only
./run_migrations.sh --check-only
```

## Migration Script Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message |
| `--check-only` | Only check migration status, don't run migrations |
| `--force` | Force run migrations even if not needed |
| (no args) | Normal operation: check and run if needed |

## Error Handling

The migration system handles various error scenarios:

1. **Database Unavailable**: Retries with exponential backoff
2. **Migration Failures**: Logs errors and continues (in Docker)
3. **Permission Issues**: Clear error messages with resolution steps
4. **Script Not Found**: Graceful fallback to alternative methods

## Logging

The migration script provides detailed logging with:

- **Timestamps**: All log entries include timestamps
- **Color Coding**: Different colors for different log levels
- **Progress Indicators**: Clear indication of current operation
- **Error Details**: Detailed error messages for troubleshooting

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if PostgreSQL is running
   - Verify DATABASE_URL environment variable
   - Ensure network connectivity

2. **Migration Script Not Found**
   - Verify the script exists in `scripts/check_and_run_migrations.sh`
   - Check file permissions (should be executable)

3. **Permission Denied**
   - Ensure the script has execute permissions: `chmod +x scripts/check_and_run_migrations.sh`
   - Check user permissions for database access

### Debug Mode

To enable debug output, set the environment variable:

```bash
export DEBUG=1
./run_migrations.sh
```

## Best Practices

1. **Always Backup**: Create database backups before running migrations in production
2. **Test First**: Test migrations in a staging environment
3. **Monitor Logs**: Watch migration logs for any issues
4. **Version Control**: Keep migration files in version control
5. **Rollback Plan**: Have a rollback strategy for critical migrations

## Integration with CI/CD

The migration system can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Database Migrations
  run: |
    docker-compose run --rm migrations
```

This ensures that migrations are always run before deploying new versions of the application. 