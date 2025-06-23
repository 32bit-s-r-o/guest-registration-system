# Testing Guide Documentation

[← Back to Documentation Index](../docs/README.md)

## Overview

The Guest Registration System includes comprehensive testing coverage with automated test suites, manual testing procedures, and continuous integration support. This guide covers all aspects of testing the system to ensure reliability and functionality.

## Quick Start

```bash
# Run all tests
python manage.py test

# Run specific test categories
python test_backup_functionality.py
python test_migration_system.py
python system_test.py

# Check test coverage
python -m pytest --cov=app tests/
```

## Current System Status

- **Test Coverage**: ✅ Comprehensive
- **All Tests Passing**: ✅ 9/9 Management Script Tests
- **Automated Tests**: ✅ 7 Test Scripts Available
- **Manual Tests**: ✅ Documented Procedures
- **CI/CD Ready**: ✅ GitHub Actions Compatible

## Test Categories

### 1. Management Script Tests

**Script**: `test_manage_script.py`

**Coverage:**
- ✅ Script existence and import
- ✅ Available commands (9/9)
- ✅ Script categories (5/5)
- ✅ Help command functionality
- ✅ Status command functionality
- ✅ Migration status functionality
- ✅ Cleanup command functionality
- ✅ Invalid command handling

**Results:**
```
Tests passed: 9/9
✅ All management script tests passed!
✅ Universal management script is ready for use
```

### 2. System Integration Tests

**Script**: `system_test.py`

**Coverage:**
- Complete system workflow testing
- Guest registration process
- Admin functionality
- Database operations
- File uploads
- Email functionality

### 3. Backup System Tests

**Script**: `test_backup_functionality.py`

**Coverage:**
- System backup creation
- Monthly backup API
- Access control verification
- File format validation
- Error handling
- Guest photo exclusion

**Script**: `test_backup_api.py`

**Coverage:**
- API endpoint testing
- Parameter validation
- Response format verification
- Authentication checks

### 4. Migration System Tests

**Script**: `test_migration_system.py`

**Coverage:**
- Migration application
- Rollback functionality
- Version tracking
- Database schema changes
- Error handling

### 5. Email Functionality Tests

**Script**: `test_email_functionality.py`

**Coverage:**
- Email sending functionality
- Template rendering
- Language-specific emails
- Error handling
- SMTP configuration

### 6. CSV Export Tests

**Script**: `test_csv_export.py`

**Coverage:**
- Data export functionality
- CSV format validation
- File download testing
- Data integrity verification

### 7. Language Picker Tests

**Script**: `test_language_picker.py`

**Coverage:**
- Language switching
- Session management
- Template rendering
- URL parameter handling

## Test Commands

### Run All Tests

```bash
# Using management script
python manage.py test

# Individual test scripts
python test_manage_script.py
python system_test.py
python test_backup_functionality.py
python test_migration_system.py
python test_email_functionality.py
python test_csv_export.py
python test_language_picker.py
```

### Test Specific Features

```bash
# Test backup functionality
python test_backup_functionality.py

# Test migration system
python test_migration_system.py

# Test email system
python test_email_functionality.py
```

### Test with Coverage

```bash
# Install pytest-cov if not installed
pip install pytest-cov

# Run with coverage
python -m pytest --cov=app tests/
```

## Manual Testing Procedures

### 1. Guest Registration Workflow

**Steps:**
1. Access registration page
2. Enter trip confirmation code
3. Fill guest information
4. Upload document photos
5. Submit registration
6. Verify confirmation email

**Expected Results:**
- Registration saved to database
- Email sent to guest
- Admin notification received
- Photos uploaded successfully

### 2. Admin Dashboard Testing

**Steps:**
1. Login as admin
2. Access dashboard
3. Check statistics
4. Navigate to different sections
5. Test data management functions

**Expected Results:**
- Dashboard loads correctly
- Statistics accurate
- Navigation works
- Functions operational

### 3. Invoice System Testing

**Steps:**
1. Create new invoice
2. Add invoice items
3. Generate PDF
4. Send via email
5. Check status updates

**Expected Results:**
- Invoice created successfully
- PDF generated correctly
- Email sent with attachment
- Status updated properly

### 4. Housekeeping Testing

**Steps:**
1. Login as housekeeper
2. View assigned tasks
3. Update task status
4. Upload amenity photos
5. Mark tasks complete

**Expected Results:**
- Tasks displayed correctly
- Status updates saved
- Photos uploaded
- Completion tracked

## Automated Test Suites

### Management Script Test Suite

**File**: `test_manage_script.py`

**Test Cases:**
1. Script existence verification
2. Import functionality
3. Command availability
4. Category definitions
5. Help command functionality
6. Status command functionality
7. Migration status functionality
8. Cleanup command functionality
9. Invalid command handling

### System Integration Test Suite

**File**: `system_test.py`

**Test Cases:**
1. Database connectivity
2. User authentication
3. Guest registration
4. File uploads
5. Email sending
6. PDF generation
7. Data export
8. Admin functions

### Backup System Test Suite

**File**: `test_backup_functionality.py`

**Test Cases:**
1. System backup creation
2. Monthly backup API
3. Access control
4. File format validation
5. Error handling
6. Guest photo exclusion

## Test Data Management

### Test Data Creation

```bash
# Create test registrations
python create_test_registration.py

# Create housekeeper data
python create_housekeeper_data.py

# Reset test data
python reset_data.py
```

### Test Environment Setup

```bash
# Setup test environment
python manage.py setup

# Seed test data
python manage.py seed

# Run tests
python manage.py test
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python manage.py test
    
    - name: Run migration tests
      run: |
        python test_migration_system.py
    
    - name: Run backup tests
      run: |
        python test_backup_functionality.py
```

### Local CI Testing

```bash
# Run full test suite
python manage.py test

# Check system status
python manage.py status

# Verify migrations
python manage.py migrate status
```

## Test Coverage Analysis

### Current Coverage

- **Management Script**: 100% (9/9 tests passing)
- **System Integration**: Comprehensive workflow testing
- **Backup System**: Full functionality coverage
- **Migration System**: Complete migration testing
- **Email System**: SMTP and template testing
- **Export System**: CSV and JSON export testing
- **Language System**: Multi-language support testing

### Coverage Goals

- **Unit Tests**: 90%+ code coverage
- **Integration Tests**: All major workflows
- **System Tests**: End-to-end functionality
- **Security Tests**: Access control verification

## Performance Testing

### Load Testing

```bash
# Basic load testing
ab -n 100 -c 10 http://localhost:5000/

# Database performance
python -c "import time; start=time.time(); # test code; print(time.time()-start)"
```

### Database Performance

- Migration execution time
- Query performance
- Backup creation time
- Data export speed

## Security Testing

### Access Control Testing

```bash
# Test admin access
curl -H "Cookie: session=admin_session" http://localhost:5000/admin/dashboard

# Test unauthorized access
curl http://localhost:5000/admin/dashboard
```

### Data Protection Testing

- Guest photo exclusion
- Sensitive data handling
- Session management
- CSRF protection

## Troubleshooting

### Common Test Issues

1. **Database Connection**
   - Check database URL
   - Verify PostgreSQL running
   - Test connection manually

2. **Test Data Issues**
   - Reset test data
   - Check seed scripts
   - Verify database state

3. **Email Testing**
   - Check SMTP configuration
   - Verify email credentials
   - Test email templates

### Debug Commands

```bash
# Verbose test output
python -v test_manage_script.py

# Debug specific test
python -m pdb test_manage_script.py

# Check test environment
python manage.py status
```

## Best Practices

### Test Development

1. **Write Tests First**
   - TDD approach for new features
   - Test existing functionality
   - Maintain test coverage

2. **Test Organization**
   - Group related tests
   - Use descriptive test names
   - Maintain test data

3. **Test Maintenance**
   - Update tests with code changes
   - Remove obsolete tests
   - Keep tests fast and reliable

### Test Execution

1. **Regular Testing**
   ```bash
   # Daily testing
   python manage.py test
   
   # Before deployments
   python manage.py status
   python manage.py test
   ```

2. **Comprehensive Testing**
   ```bash
   # Full test suite
   python manage.py all
   ```

## Related Documentation

- [Universal Management Script](management-script.md) - Test execution
- [Database Migrations](migrations.md) - Migration testing
- [Backup System](backup-system.md) - Backup testing
- [Installation Guide](installation.md) - Test environment setup

## Support

For testing issues:

1. Check test environment
2. Review error logs
3. Verify test data
4. Run individual tests

## Version History

- **v1.0.0**: Initial test suite
- **v1.1.0**: Added comprehensive testing
- **v1.2.0**: Enhanced test coverage
- **v1.3.0**: CI/CD integration

---

[← Back to Documentation Index](../docs/README.md) 