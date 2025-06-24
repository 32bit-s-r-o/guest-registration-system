# Migration System Documentation

## Overview

The Guest Registration System includes an automated migration and setup system that ensures the database schema is always up to date and properly initialized. The system consists of:

1. **Migration Script**: `scripts/check_and_run_migrations.sh` - Main migration orchestration script
2. **Wrapper Script**: `run_migrations.sh` - Simple wrapper for easy access
3. **Setup Integration**: Automatic setup script execution for new installations
4. **Docker Integration**: Automatic setup and migration execution in the main application container
5. **Python Migration System**: `migrations.py` - Core migration logic

## How It Works

### Automatic Setup and Migration in Docker

When running the application with Docker Compose, setup and migrations are automatically handled in the main application container:

1. **Application Startup**: The main app container starts
2. **Database Health Check**: The system waits for the database to be healthy
3. **Setup Detection**: Checks if database is empty and needs setup
4. **Setup Execution**: Runs setup if needed (creates tables + admin user)
5. **Migration Check**: Checks if migrations are needed
6. **Migration Execution**: Runs migrations if needed
7. **Application Start**: Starts the main application

### Manual Execution

You can run setup and migrations manually using the provided scripts:

```bash
# Run setup and migrations with automatic checks
./run_migrations.sh

# Run setup only
./run_migrations.sh --setup-only

# Run migrations only (skip setup)
./run_migrations.sh --migrate-only

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

### Setup Detection and Execution

The script intelligently detects:
- Whether the database is empty (needs setup)
- If setup has already been completed
- Whether to run in interactive or non-interactive mode

### Migration Status Detection

The script intelligently detects:
- Whether migrations are needed
- Current database version
- Pending migrations
- Migration history

### Safe Execution

Setup and migrations are executed safely with:
- Error handling and rollback capabilities
- Verification after execution
- Detailed logging with colored output
- Non-blocking execution (continues even if setup/migrations fail)
- Automatic admin user creation in Docker environments

## Docker Integration

### Docker Compose Setup

The `docker-compose.yml` includes a simplified structure:

```yaml
# Main Application (includes setup and migrations)
app:
  build:
    context: .
    dockerfile: Dockerfile
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
  # Setup and migrations run automatically on startup
```

### Dockerfile Integration

The Dockerfile includes an entrypoint script that:
1. Runs setup and migration checks before starting the application
2. Continues even if setup/migrations fail (for development)
3. Provides clear logging of the setup and migration process

## Setup Process

### What Setup Does

The setup process includes:

1. **Environment Check**: Verifies required environment variables
2. **Database Connection Test**: Ensures database is accessible
3. **Table Creation**: Creates all necessary database tables
4. **Admin User Creation**: Creates the first admin user

### Admin User Creation

In Docker environments, a default admin user is automatically created:
- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@example.com`
- **Role**: `admin`

**Important**: Change these credentials after first login in production!

### Interactive vs Non-Interactive Mode

- **Interactive Mode**: Prompts for admin user details (local development)
- **Non-Interactive Mode**: Uses default credentials (Docker environments)

## Usage Examples

### Development Environment

```bash
# Start the entire stack with automatic setup and migrations
docker-compose up

# Run setup manually
docker-compose run --rm app /app/scripts/check_and_run_migrations.sh --setup-only

# Run migrations manually
docker-compose run --rm app /app/scripts/check_and_run_migrations.sh --migrate-only

# Check migration status
docker-compose run --rm app /app/scripts/check_and_run_migrations.sh --check-only
```

### Production Environment

```bash
# Deploy with automatic setup and migrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Run setup manually in production
docker-compose exec app /app/scripts/check_and_run_migrations.sh --setup-only

# Run migrations manually in production
docker-compose exec app /app/scripts/check_and_run_migrations.sh --migrate-only
```

### Local Development

```bash
# Run setup and migrations locally (requires database connection)
./run_migrations.sh

# Run setup only
./run_migrations.sh --setup-only

# Run migrations only
./run_migrations.sh --migrate-only

# Check status only
./run_migrations.sh --check-only
```

## Migration Script Options

| Option | Description |
|--------|-------------|
| `--help`, `-h` | Show help message |
| `--check-only` | Only check migration status, don't run migrations |
| `--force` | Force run migrations even if not needed |
| `--setup-only` | Only run setup script |
| `--migrate-only` | Only run migrations, skip setup |
| (no args) | Normal operation: check setup, run if needed, then check and run migrations |

## Error Handling

The migration system handles various error scenarios:

1. **Database Unavailable**: Retries with exponential backoff
2. **Setup Failures**: Logs errors and continues (in Docker)
3. **Migration Failures**: Logs errors and continues (in Docker)
4. **Permission Issues**: Clear error messages with resolution steps
5. **Script Not Found**: Graceful fallback to alternative methods

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

2. **Setup Script Not Found**
   - Verify the script exists in `setup.py`
   - Check file permissions

3. **Migration Script Not Found**
   - Verify the script exists in `scripts/check_and_run_migrations.sh`
   - Check file permissions (should be executable)

4. **Permission Denied**
   - Ensure the script has execute permissions: `chmod +x scripts/check_and_run_migrations.sh`
   - Check user permissions for database access

5. **Admin User Creation Failed**
   - Check if admin user already exists
   - Verify database permissions
   - Check for any constraint violations

### Debug Mode

To enable debug output, set the environment variable:

```bash
export DEBUG=1
./run_migrations.sh
```

## Best Practices

1. **Always Backup**: Create database backups before running setup/migrations in production
2. **Test First**: Test setup and migrations in a staging environment
3. **Monitor Logs**: Watch setup and migration logs for any issues
4. **Version Control**: Keep setup and migration files in version control
5. **Rollback Plan**: Have a rollback strategy for critical setup/migrations
6. **Change Default Credentials**: Always change default admin credentials in production
7. **Environment Variables**: Ensure all required environment variables are set

## Integration with CI/CD

The migration system can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Setup and Run Database Migrations
  run: |
    docker-compose run --rm app /app/scripts/check_and_run_migrations.sh
```

This ensures that setup and migrations are always run before deploying new versions of the application.

## Security Considerations

1. **Default Credentials**: Change default admin credentials immediately after setup
2. **Environment Variables**: Use secure environment variables for sensitive data
3. **Database Permissions**: Ensure proper database user permissions
4. **Network Security**: Use proper network isolation in production
5. **Log Security**: Avoid logging sensitive information

## Benefits of Simplified Approach

### Advantages

1. **Single Container**: Everything runs in one container, reducing complexity
2. **Faster Startup**: No need to wait for separate setup/migration containers
3. **Simpler Dependencies**: Fewer service dependencies to manage
4. **Easier Debugging**: All logs in one place
5. **Resource Efficient**: Uses less memory and CPU
6. **Simpler Deployment**: Fewer moving parts to deploy and maintain

### How It Works

The main application container now:
1. Starts up
2. Waits for database to be healthy
3. Runs setup if needed
4. Runs migrations if needed
5. Starts the application

This approach is much more efficient and easier to manage while providing the same functionality. 