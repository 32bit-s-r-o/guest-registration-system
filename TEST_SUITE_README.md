# Test Suite for Guest Registration System

This test suite provides a comprehensive testing environment with custom configuration, seeded data, and isolated testing.

## 🚀 Quick Start

### Run Complete Test Suite
```bash
python run_test_suite.py
```

This will:
1. Set up test environment (custom port, table prefix, database)
2. Seed comprehensive test data
3. Start test server on port 5001
4. Run all tests against the test server
5. Provide detailed summary

### Run Individual Components

#### Setup Test Environment Only
```bash
python run_test_suite.py setup
```

#### Seed Test Data Only
```bash
python run_test_suite.py seed
```

#### Start Test Server Only
```bash
python run_test_suite.py server
```

#### Clean Up Test Environment
```bash
python run_test_suite.py cleanup
```

## 🔧 Test Configuration

### Test Environment Settings
- **Port**: 5001 (separate from production)
- **Database**: `guest_registration_test`
- **Table Prefix**: `test_guest_reg_`
- **Upload Folder**: `test_uploads`
- **Server URL**: `http://localhost:5001`

### Test Admin Credentials
- **Username**: `test_admin`
- **Password**: `test_password123`
- **Email**: `test_admin@example.com`

### Test Data
- **5 Trips** with different dates and confirmation codes
- **10 Registrations** with various statuses (pending, approved, rejected)
- **20 Guests** with different age categories and documents
- **8 Invoices** with different statuses and amounts

## 📁 Test Files

### Core Test Files
- `test_config.py` - Test configuration and environment setup
- `test_seeder.py` - Comprehensive test data seeder
- `test_server.py` - Test server runner
- `run_test_suite.py` - Complete test suite runner
- `test_runner.py` - Simple test runner for individual tests

### Test Scripts
- `test_backup_api.py` - Backup API functionality
- `test_backup_functionality.py` - Backup system tests
- `test_migration_system.py` - Migration system tests
- `system_test.py` - Comprehensive system tests
- `test_email_functionality.py` - Email functionality tests
- `test_csv_export.py` - CSV export tests
- `test_language_picker.py` - Language picker tests
- `test_fixes.py` - Bug fix verification tests
- `test_refactor.py` - Refactor verification tests
- `test_standalone.py` - Standalone functionality tests
- `test_server_url.py` - Server URL configuration tests

## 🧪 Running Tests

### Method 1: Complete Test Suite (Recommended)
```bash
python run_test_suite.py
```

### Method 2: Individual Test with Test Environment
```bash
python test_runner.py system_test.py
```

### Method 3: Manual Setup and Run
```bash
# 1. Setup environment
python run_test_suite.py setup

# 2. Start server
python run_test_suite.py server

# 3. In another terminal, run tests
python test_runner.py update  # Update test scripts
python system_test.py         # Run specific test
```

## 🌐 Test Server Access

Once the test server is running:

- **Main URL**: http://localhost:5001
- **Admin Login**: http://localhost:5001/admin/login
- **Dashboard**: http://localhost:5001/admin/dashboard
- **Test Data**: Pre-seeded with comprehensive test data

## 📊 Test Data Overview

### Trips
- Mountain Retreat - Test Trip 1
- Beach House - Test Trip 2
- City Apartment - Test Trip 3
- Country Villa - Test Trip 4
- Lakeside Cabin - Test Trip 5

### Registrations
- 10 registrations with various statuses
- Mix of languages (English, Czech, Slovak)
- Different guest counts (1-3 guests per registration)

### Guests
- 20 guests with realistic names
- Mix of adults and children
- Various document types and numbers
- GDPR consent properly set

### Invoices
- 8 invoices with different statuses
- Various amounts and currencies
- Different client information
- Invoice items for each invoice

## 🔍 Test Environment Isolation

### Database Isolation
- Uses separate test database: `guest_registration_test`
- Uses test table prefix: `test_guest_reg_`
- No interference with production data

### Port Isolation
- Test server runs on port 5001
- Production server can run on port 5000
- No port conflicts

### File Isolation
- Test uploads go to `test_uploads/` directory
- Separate from production uploads
- Automatic cleanup after tests

## 🧹 Cleanup

### Automatic Cleanup
The test suite automatically cleans up:
- Test environment variables
- Test server process
- Temporary files

### Manual Cleanup
```bash
python run_test_suite.py cleanup
```

### Clear Test Data
```bash
python test_seeder.py clear
```

## 📈 Test Results

### Success Criteria
- **90%+ Success Rate**: Excellent
- **80-89% Success Rate**: Good
- **<80% Success Rate**: Needs attention

### Test Summary
The test suite provides:
- Total test count
- Pass/fail statistics
- Success rate percentage
- Detailed error reporting
- Test execution times

## 🔧 Customization

### Modify Test Configuration
Edit `test_config.py` to change:
- Test port number
- Table prefix
- Database name
- Test data quantities
- Admin credentials

### Add New Tests
1. Create test script following existing patterns
2. Add to test suite in `run_test_suite.py`
3. Update `test_runner.py` if needed

### Modify Test Data
Edit `test_seeder.py` to:
- Change test data quantities
- Modify test data content
- Add new data types

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using port 5001
lsof -i :5001

# Kill process if needed
kill -9 <PID>
```

#### Database Connection Issues
- Verify PostgreSQL is running
- Check connection credentials in `test_config.py`
- Ensure test database exists

#### Test Data Issues
```bash
# Clear and reseed test data
python test_seeder.py clear
python test_seeder.py
```

#### Environment Issues
```bash
# Reset test environment
python run_test_suite.py cleanup
python run_test_suite.py setup
```

## 📝 Best Practices

1. **Always use test environment** for testing
2. **Don't run tests against production** data
3. **Clean up after testing** (automatic with test suite)
4. **Check test results** carefully
5. **Update test data** when adding new features
6. **Use isolated test database** for development

## 🎯 Benefits

- **Isolated Testing**: No interference with production
- **Comprehensive Data**: Realistic test scenarios
- **Automated Setup**: One-command test execution
- **Detailed Reporting**: Clear success/failure information
- **Easy Debugging**: Access to test server and data
- **Consistent Environment**: Same setup every time 