# Quick Start Guide

[← Back to Documentation Index](README.md)

## Get Up and Running in 5 Minutes

This guide will help you get the Guest Registration System running quickly for development or testing purposes.

## Prerequisites Check

Before starting, ensure you have:

- ✅ Python 3.7+ installed
- ✅ PostgreSQL 12+ installed and running
- ✅ Git installed

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone https://github.com/32bit-s-r-o/guest-registration-system.git
cd guest-registration-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Database Setup

```bash
# Create database
sudo -u postgres createdb airbnb_guests

# Or if you have a different PostgreSQL setup:
createdb airbnb_guests
```

## Step 3: Configuration

```bash
# Copy and edit configuration
cp config.env.example config.env
nano config.env
```

**Minimum Configuration:**
```bash
DATABASE_URL=postgresql://localhost/airbnb_guests
SECRET_KEY=your-secret-key-here
```

## Step 4: Initialize System

```bash
# Run the universal setup command
python manage.py setup
```

This single command will:
- ✅ Create necessary directories
- ✅ Apply database migrations
- ✅ Create sample data
- ✅ Run system tests
- ✅ Create initial backup

## Step 5: Start the Application

```bash
# Start the Flask application with default settings
python app.py

# Or customize the startup parameters:
python app.py --port 8080 --host 0.0.0.0 --threaded
python app.py --debug --reload --port 5000
python app.py --no-debug --port 80
```

### Available Startup Parameters

The Flask application supports various command-line parameters for flexible deployment:

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

### Common Usage Examples

```bash
# Development with auto-reload
python app.py --debug --reload --port 5000

# Production server (accessible from network)
python app.py --host 0.0.0.0 --port 80 --no-debug --threaded

# HTTPS with self-signed certificate
python app.py --ssl-context adhoc --port 443

# Custom port for testing
python app.py --port 8080
```

### Parameter Testing

Test the parameter functionality:

```bash
# Run parameter tests
python test_app_parameters.py
```

This will test various parameter combinations and verify the app starts correctly with each configuration.

## Step 6: Access the System

Open your browser and navigate to:

- **Main Site**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin/login

**Default Admin Credentials:**
- Username: `admin`
- Password: `admin123`

## Verify Installation

### Check System Status

```bash
python manage.py status
```

**Expected Output:**
```
📊 System Status
==================================================
✅ Flask application is running
📊 Database Version: 000001
📊 Applied Migrations: 2
📊 Pending Migrations: 0

📁 Available Scripts:
  Tests: 7 scripts
  Migrations: 1 scripts
  Seeds: 2 scripts
  Backups: 1 scripts
  Utilities: 10 scripts
```

### Run Tests

```bash
python manage.py test
```

**Expected Output:**
```
Tests passed: 9/9
✅ All management script tests passed!
```

## Quick Commands Reference

### System Management

```bash
# Check status
python manage.py status

# Run all tests
python manage.py test

# Apply migrations
python manage.py migrate migrate

# Create backup
python manage.py backup

# Clean up system
python manage.py clean
```

### Development Commands

```bash
# Start development server
python app.py

# Run specific tests
python test_backup_functionality.py
python test_migration_system.py

# Check migration status
python manage.py migrate status
```

## First Steps

### 1. Create a Trip

1. Login to admin panel
2. Navigate to "Trips" → "New Trip"
3. Fill in trip details
4. Save the trip

### 2. Test Guest Registration

1. Copy the trip confirmation code
2. Visit the main site
3. Enter the confirmation code
4. Complete guest registration

### 3. Test Admin Functions

1. View registrations
2. Approve/reject registrations
3. Generate invoices
4. Export data

## Common Issues & Solutions

### Issue: Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Create database if it doesn't exist
createdb airbnb_guests
```

### Issue: Port Already in Use

```bash
# Check what's using port 5000
lsof -i :5000

# Kill the process or use different port
python app.py --port 5000
```

### Issue: Permission Denied

```bash
# Fix upload directory permissions
chmod 755 uploads/
chown -R $USER:$USER uploads/
```

### Issue: Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version
```

## Development Workflow

### Daily Development

```bash
# Start development
source venv/bin/activate
python app.py

# In another terminal, run tests
python manage.py test
```

### Before Committing

```bash
# Run all tests
python manage.py test

# Check system status
python manage.py status

# Clean up
python manage.py clean
```

### After Pulling Changes

```bash
# Update dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate migrate

# Run tests
python manage.py test
```

## System Features Overview

### ✅ What's Working

- **Guest Registration**: Complete workflow with document uploads
- **Admin Dashboard**: Full administrative interface
- **Trip Management**: Create and manage accommodation trips
- **Invoice System**: Generate and email PDF invoices
- **Housekeeping**: Task management for cleaning staff
- **Data Export**: CSV and JSON export functionality
- **Multi-language**: English and Czech support
- **Backup System**: Automated backup and restore
- **Migration System**: Database versioning and rollbacks

### 🚀 Ready to Use

- **Universal Management Script**: Single command-line interface
- **Comprehensive Testing**: 9/9 tests passing
- **Production Ready**: Secure and scalable
- **Documentation**: Complete guides and examples

## Next Steps

### For Development

1. **Explore the Codebase**
   - Review `app.py` for main application logic
   - Check `templates/` for frontend templates
   - Examine `migrations/` for database schema

2. **Customize the System**
   - Modify templates for branding
   - Add new features
   - Customize email templates

3. **Extend Functionality**
   - Add new data export formats
   - Implement additional payment methods
   - Create new admin features

### For Production

1. **Security Hardening**
   - Change default passwords
   - Configure SSL/TLS
   - Set up proper backups

2. **Performance Optimization**
   - Configure database indexes
   - Set up caching
   - Optimize file uploads

3. **Monitoring Setup**
   - Configure logging
   - Set up health checks
   - Monitor system performance

## Support

### Getting Help

- **Documentation**: Check the [main documentation](README.md)
- **Issues**: Create an issue in the repository
- **Questions**: Review the troubleshooting section

### Useful Links

- [Installation Guide](installation.md) - Detailed installation
- [Configuration Guide](configuration.md) - Environment setup
- [Universal Management Script](management-script.md) - System management
- [API Documentation](api.md) - REST API reference

---

**You're all set!** 🎉

The Guest Registration System is now running and ready for use. Start exploring the features and customizing the system for your needs.

[← Back to Documentation Index](README.md) 