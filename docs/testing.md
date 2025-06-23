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

# Test language support
python test_language_picker.py
python test_slovak_language.py

# Test housekeeping features
python test_amenity_housekeeper_system.py

# Check test coverage
python -m pytest --cov=app tests/
```

## Current System Status

- **Test Coverage**: ✅ Comprehensive
- **All Tests Passing**: ✅ 9/9 Management Script Tests
- **Automated Tests**: ✅ 10 Test Scripts Available
- **Manual Tests**: ✅ Documented Procedures
- **CI/CD Ready**: ✅ GitHub Actions Compatible
- **Language Support**: ✅ English, Czech, Slovak
- **Housekeeping System**: ✅ Complete testing coverage

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
- Language switching
- Housekeeping features

### 3. Language Support Tests

**Script**: `test_language_picker.py`

**Coverage:**
- Language picker configuration
- Enable/disable functionality
- Supported locales verification
- Configuration instructions

**Script**: `test_slovak_language.py`

**Coverage:**
- Slovak language switching
- Language picker functionality
- Three-language support (EN, CS, SK)
- Navigation and UI testing

### 4. Housekeeping System Tests

**Script**: `test_amenity_housekeeper_system.py`

**Coverage:**
- Amenity management
- Housekeeper assignments
- Task creation and management
- Photo upload functionality
- Bulk operations
- Status updates

### 5. Backup System Tests

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

### 6. Migration System Tests

**Script**: `test_migration_system.py`

**Coverage:**
- Migration application
- Rollback functionality
- Version tracking
- Database schema changes
- Error handling

### 7. Email Functionality Tests

**Script**: `test_email_functionality.py`

**Coverage:**
- Email sending functionality
- Template rendering
- Language-specific emails
- Error handling
- SMTP configuration

### 8. CSV Export Tests

**Script**: `test_csv_export.py`

**Coverage:**
- Data export functionality
- CSV format validation
- File download testing
- Data integrity verification

### 9. Date Format Tests

**Script**: `test_date_format_settings.py`

**Coverage:**
- User date format preferences
- Date formatting functionality
- Template rendering
- Format conversion

### 10. Airbnb Integration Tests

**Script**: `test_airbnb_sync.py`

**Coverage:**
- Airbnb calendar sync
- Reservation parsing
- Confirmation code extraction
- Multi-calendar support

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
python test_slovak_language.py
python test_amenity_housekeeper_system.py
python test_date_format_settings.py
python test_airbnb_sync.py
```

### Test Specific Features

```bash
# Test backup functionality
python test_backup_functionality.py

# Test migration system
python test_migration_system.py

# Test email system
python test_email_functionality.py

# Test language support
python test_language_picker.py
python test_slovak_language.py

# Test housekeeping system
python test_amenity_housekeeper_system.py

# Test date formatting
python test_date_format_settings.py

# Test Airbnb integration
python test_airbnb_sync.py
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

```