# Configuration Guide

[← Back to Documentation Index](README.md)

## Overview

This guide covers all configuration options for the Guest Registration System, including environment variables, database settings, email configuration, and system preferences.

## Environment Variables

### Basic Configuration

Copy the example configuration file and customize it for your environment:

```bash
cp config.env.example config.env
```

### Required Variables

#### Database Configuration

```bash
# PostgreSQL database connection
DATABASE_URL=postgresql://username:password@host:port/database_name

# Examples:
DATABASE_URL=postgresql://localhost/airbnb_guests
DATABASE_URL=postgresql://user:pass@localhost:5432/airbnb_guests
DATABASE_URL=postgresql://user:pass@prod-server.com:5432/airbnb_guests
```

#### Flask Configuration

```bash
# Flask secret key (required for sessions)
SECRET_KEY=your-super-secret-key-here

# Flask environment
FLASK_ENV=development  # or production
FLASK_DEBUG=True       # or False for production
```

### Optional Variables

#### Email Configuration

```bash
# SMTP server settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Alternative: SMTP with SSL
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### Table Prefix Configuration

```bash
# Database table prefix (default: guest_reg_)
TABLE_PREFIX=guest_reg_
```

#### Language Configuration

```bash
# Enable/disable language picker
LANGUAGE_PICKER_ENABLED=true  # or false
```

#### File Upload Configuration

```bash
# Upload folder path
UPLOAD_FOLDER=uploads

# Maximum file size (default: 16MB)
MAX_CONTENT_LENGTH=16777216
```

## Configuration Examples

### Development Configuration

```bash
# Development environment
DATABASE_URL=postgresql://localhost/airbnb_guests_dev
SECRET_KEY=dev-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=dev@example.com
MAIL_PASSWORD=dev-password
TABLE_PREFIX=guest_reg_
LANGUAGE_PICKER_ENABLED=true
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Production Configuration

```bash
# Production environment
DATABASE_URL=postgresql://prod_user:prod_pass@prod-db.com:5432/airbnb_guests_prod
SECRET_KEY=your-super-secure-production-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=admin@yourcompany.com
MAIL_PASSWORD=your-app-password
TABLE_PREFIX=guest_reg_
LANGUAGE_PICKER_ENABLED=true
UPLOAD_FOLDER=/var/www/uploads
MAX_CONTENT_LENGTH=16777216
```

### Docker Configuration

```bash
# Docker environment
DATABASE_URL=postgresql://postgres:password@db:5432/airbnb_guests
SECRET_KEY=docker-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=docker@example.com
MAIL_PASSWORD=docker-password
TABLE_PREFIX=guest_reg_
LANGUAGE_PICKER_ENABLED=true
UPLOAD_FOLDER=/app/uploads
MAX_CONTENT_LENGTH=16777216
```

## Database Configuration

### PostgreSQL Setup

#### Local Development

```bash
# Create database
createdb airbnb_guests

# Create user (optional)
createuser --interactive airbnb_user

# Grant permissions
psql -d airbnb_guests -c "GRANT ALL PRIVILEGES ON DATABASE airbnb_guests TO airbnb_user;"
```

#### Production Database

```bash
# Create production database
sudo -u postgres createdb airbnb_guests_prod

# Create production user
sudo -u postgres createuser --interactive airbnb_prod

# Set password
sudo -u postgres psql -c "ALTER USER airbnb_prod PASSWORD 'secure_password';"

# Grant permissions
sudo -u postgres psql -d airbnb_guests_prod -c "GRANT ALL PRIVILEGES ON DATABASE airbnb_guests_prod TO airbnb_prod;"
```

### Connection String Format

```
postgresql://username:password@host:port/database_name
```

**Components:**
- `username`: Database username
- `password`: Database password
- `host`: Database host (localhost, IP, or domain)
- `port`: Database port (default: 5432)
- `database_name`: Database name

## Email Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication**
2. **Generate App Password**
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"

3. **Configuration**
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
```

### Other SMTP Providers

#### Outlook/Hotmail
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

#### Yahoo Mail
```bash
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
```

#### Custom SMTP Server
```bash
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-username
MAIL_PASSWORD=your-password
```

### Email Testing

```bash
# Test email configuration
python test_email_functionality.py

# Check email settings
python manage.py status
```

## Security Configuration

### Secret Key Generation

Generate a secure secret key:

```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using OpenSSL
openssl rand -hex 32

# Using online generator
# Visit: https://generate-secret.vercel.app/32
```

### Production Security

```bash
# Use strong secret key
SECRET_KEY=your-64-character-secret-key

# Disable debug mode
FLASK_DEBUG=False
FLASK_ENV=production

# Use HTTPS
# Configure SSL/TLS in web server (Nginx/Apache)

# Secure database connection
DATABASE_URL=postgresql://user:strong_password@host:5432/db?sslmode=require
```

## File Upload Configuration

### Upload Directory

```bash
# Set upload directory
UPLOAD_FOLDER=uploads

# Create directory with proper permissions
mkdir -p uploads
chmod 755 uploads
chown www-data:www-data uploads  # For production
```

### File Size Limits

```bash
# Maximum file size (16MB default)
MAX_CONTENT_LENGTH=16777216

# Alternative sizes:
MAX_CONTENT_LENGTH=8388608   # 8MB
MAX_CONTENT_LENGTH=33554432  # 32MB
```

### Allowed File Types

The system accepts these image formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)

## Language Configuration

### Multi-language Support

```bash
# Enable language picker
LANGUAGE_PICKER_ENABLED=true

# Disable language picker (English only)
LANGUAGE_PICKER_ENABLED=false
```

### Supported Languages

- **English (en)**: Default language
- **Czech (cs)**: Secondary language

### Adding New Languages

1. **Create translation directory**
   ```bash
   mkdir -p translations/xx/LC_MESSAGES
   ```

2. **Extract messages**
   ```bash
   python extract_translations.py
   ```

3. **Add language to configuration**
   ```python
   app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'cs', 'xx']
   ```

## Table Prefix Configuration

### Custom Table Prefix

```bash
# Use custom prefix
TABLE_PREFIX=my_app_

# This creates tables like:
# my_app_user
# my_app_trip
# my_app_registration
# my_app_guest
```

### Default Prefix

```bash
# Default prefix
TABLE_PREFIX=guest_reg_

# Creates tables like:
# guest_reg_user
# guest_reg_trip
# guest_reg_registration
# guest_reg_guest
```

## Environment-Specific Configuration

### Development Environment

```bash
# Development settings
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=postgresql://localhost/airbnb_guests_dev
SECRET_KEY=dev-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=dev@example.com
MAIL_PASSWORD=dev-password
LANGUAGE_PICKER_ENABLED=true
```

### Testing Environment

```bash
# Testing settings
FLASK_ENV=testing
FLASK_DEBUG=True
DATABASE_URL=postgresql://localhost/airbnb_guests_test
SECRET_KEY=test-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=test@example.com
MAIL_PASSWORD=test-password
LANGUAGE_PICKER_ENABLED=true
```

### Production Environment

```bash
# Production settings
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://prod_user:prod_pass@prod-db.com:5432/airbnb_guests_prod
SECRET_KEY=your-super-secure-production-secret-key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=admin@yourcompany.com
MAIL_PASSWORD=your-app-password
LANGUAGE_PICKER_ENABLED=true
```

## Configuration Validation

### Check Configuration

```bash
# Validate configuration
python manage.py status

# Expected output:
# ✅ Flask application is running
# 📊 Database Version: 000001
# 📊 Applied Migrations: 2
# 📊 Pending Migrations: 0
```

### Test Configuration

```bash
# Test database connection
python -c "from app import db; print('Database OK')"

# Test email configuration
python test_email_functionality.py

# Test file uploads
python -c "from app import app; print('Upload config OK')"
```

## Troubleshooting

### Common Configuration Issues

1. **Database Connection Error**
   ```bash
   # Check database URL format
   echo $DATABASE_URL
   
   # Test connection
   psql $DATABASE_URL -c "SELECT 1;"
   ```

2. **Email Configuration Error**
   ```bash
   # Check email settings
   python test_email_functionality.py
   
   # Verify SMTP credentials
   telnet smtp.gmail.com 587
   ```

3. **File Upload Issues**
   ```bash
   # Check upload directory
   ls -la uploads/
   
   # Check permissions
   chmod 755 uploads/
   ```

4. **Secret Key Issues**
   ```bash
   # Generate new secret key
   python -c "import secrets; print(secrets.token_hex(32))"
   
   # Update configuration
   nano config.env
   ```

### Debug Configuration

```bash
# Enable debug mode
export FLASK_DEBUG=True
export FLASK_ENV=development

# Run with debug
python app.py
```

## Best Practices

### Security Best Practices

1. **Use Strong Secret Keys**
   - Generate 64-character random keys
   - Never use default keys in production
   - Rotate keys regularly

2. **Secure Database Connections**
   - Use strong passwords
   - Enable SSL/TLS
   - Restrict database access

3. **Email Security**
   - Use app passwords for Gmail
   - Enable 2FA on email accounts
   - Use secure SMTP connections

4. **File Upload Security**
   - Validate file types
   - Limit file sizes
   - Secure upload directory

### Configuration Management

1. **Environment Separation**
   - Use different configs for dev/test/prod
   - Never commit production secrets
   - Use environment variables

2. **Backup Configuration**
   - Backup configuration files
   - Document configuration changes
   - Version control configuration templates

3. **Monitoring Configuration**
   - Log configuration changes
   - Monitor configuration errors
   - Alert on configuration issues

## Related Documentation

- [Installation Guide](installation.md) - System installation
- [Quick Start Guide](quick-start.md) - Quick setup
- [Universal Management Script](management-script.md) - System management
- [Deployment Guide](deployment.md) - Production deployment

## Support

For configuration issues:

1. Check environment variables
2. Verify database connectivity
3. Test email configuration
4. Review error logs

---

[← Back to Documentation Index](README.md) 