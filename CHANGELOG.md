# Changelog

All notable changes to the Guest Registration System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.9.4] - 2025-06-25

### Added
- **Production Lock Feature**
  - Added production environment detection to prevent accidental database seeding/reset operations
  - Implemented `check_production_lock()` utility function with comprehensive environment checks
  - Added `ALLOW_PRODUCTION_SEED` environment variable override for emergency situations
  - Enhanced security by blocking destructive operations in production environments
  - Added production lock test to comprehensive test suite for validation

- **Trip Management Enhancements**
  - Added ability to delete all registrations for a specific trip
  - Implemented new route `/admin/trips/<id>/delete-registrations` with proper access control
  - Enhanced admin interface with registration management capabilities
  - Added confirmation dialog for bulk registration deletion
  - Improved trip edit page with registration management options

### Fixed
- **Trip Edit Page Routing**
  - Fixed critical routing error on trip edit page (`update_trip` endpoint not found)
  - Corrected form action URL from `trips.update_trip` to `trips.edit_trip`
  - Resolved `werkzeug.routing.exceptions.BuildError` preventing trip editing
  - Enhanced trip edit functionality with proper form submission

### Technical Improvements
- **Production Safety**
  - Implemented comprehensive production environment detection
  - Added environment variable checks for FLASK_ENV, DOCKER_ENV, DATABASE_URL patterns
  - Enhanced error messages with clear guidance for production lock bypass
  - Added production lock to all seeding and reset operations across the application

- **Code Quality**
  - Added production lock checks to admin blueprint, CLI scripts, and management tools
  - Enhanced error handling and user feedback for production operations
  - Improved code organization with centralized production lock utilities
  - Added comprehensive documentation for production lock configuration

- **Testing Enhancements**
  - Added `test_production_lock.py` to comprehensive test suite
  - Enhanced test coverage for production environment detection
  - Improved test validation for production lock functionality
  - Added test scenarios for production lock override mechanisms

### Documentation
- **Configuration Guide Updates**
  - Added production lock configuration section to `docs/configuration.md`
  - Documented `ALLOW_PRODUCTION_SEED` environment variable usage
  - Added best practices for production environment management
  - Enhanced security guidelines for database operations

## [1.9.3] - 2025-06-25

### Fixed
- **Invoice Status Change Functionality**
  - Fixed invoice status change not working on both list and detail pages
  - Corrected JavaScript route URLs from `/admin/invoices/<id>/status` to `/admin/invoices/<id>/change-status`
  - Updated form data format from JSON to URL-encoded for better compatibility with Flask routes
  - Enhanced error handling and user feedback for status changes

- **PDF Generation in Docker**
  - Fixed WeasyPrint PDF generation compatibility issues in Docker containers
  - Updated WeasyPrint from version 59.0 to 60.2 with pydyf 0.10.0 for stable PDF generation
  - Resolved `TypeError: PDF.__init__() takes 1 positional argument but 3 were given` error
  - Updated both requirements.txt and Dockerfile to use compatible library versions

- **Invoice PDF Rendering**
  - Improved invoice PDF rendering with proper line breaks for multi-line fields
  - Fixed notes and address fields displaying `<br>` tags instead of actual line breaks
  - Enhanced PDF template to properly render newlines as line breaks using `.replace('\\n', '<br>') | safe`
  - Improved overall PDF formatting and readability

### Technical Improvements
- **Frontend JavaScript**
  - Standardized fetch API usage across invoice status change functionality
  - Improved error handling in client-side status update operations
  - Enhanced user experience with proper loading states and feedback

- **Docker Container Compatibility**
  - Ensured WeasyPrint library compatibility across different Python environments
  - Fixed package version conflicts in Docker build process
  - Enhanced container stability for PDF generation operations

## [1.9.2] - 2025-06-25

### Fixed
- **PostgreSQL Database Connection Issues**
  - Resolved circular import problems in blueprint modules
  - Fixed migration manager initialization causing premature database connections
  - Updated blueprint imports to use proper lazy loading pattern
  - Moved `get_migration_manager()` function to migrations.py to avoid circular imports

- **Database Migration System**
  - Fixed database migration system for development environment
  - Added complete PostgreSQL DATABASE_URL to .env file configuration
  - Enhanced migration script to properly load environment variables
  - Improved database connection reliability and error handling

- **Data Seeding and Reset Scripts**
  - Updated reset_data.py script with correct field names (is_externally_synced, external_guest_*, etc.)
  - Added amenity creation and assignment to trip seeding process
  - Fixed field name mismatches between database models and seeding scripts
  - Enhanced sample data creation with proper amenity relationships

- **Test Suite Improvements**
  - Enhanced test suite with proper database isolation
  - Fixed test environment setup for both SQLite and PostgreSQL
  - Improved test reliability and consistency
  - Better integration with management script

### Technical Improvements
- **Application Startup Reliability**
  - Improved application startup process
  - Enhanced error handling during initialization
  - Better separation of concerns in blueprint modules
  - Improved code organization and maintainability

- **Database Schema Compatibility**
  - Ensured compatibility with existing database schema
  - Maintained backward compatibility with existing data
  - Enhanced migration system reliability
  - Improved database connection management

## [1.9.1] - 2025-06-24

### Fixed
- Migration system now dynamically replaces table prefix in migration SQL files, enabling true test database isolation.
- Test suite now creates and migrates tables with the correct test prefix (`test_guest_reg_`), preventing interference with production data.
- Added logic to reset test database and re-apply migrations for prefix changes.

## [1.9.0] - 2025-01-24

### Added
- **Blueprint-Based Architecture**
  - Completed refactor from monolithic to modular blueprint structure
  - Organized code into logical blueprints: main, auth, admin, registration, etc.
  - Enhanced code organization and maintainability
  - Improved separation of concerns across application modules

- **Enhanced Test Coverage**
  - Added comprehensive test coverage for refactored components
  - Created new test scripts: `test_fixes.py`, `test_refactor.py`, `test_standalone.py`
  - Integrated new tests into the universal management script
  - Enhanced test validation for blueprint registration and functionality

- **Documentation Updates**
  - Updated all documentation to reflect new blueprint-based architecture
  - Removed references to old monolithic structure
  - Enhanced documentation clarity and accuracy
  - Updated system architecture descriptions

### Changed
- **Application Structure**
  - Restructured from single `app_old.py` file to organized blueprint modules
  - Improved code modularity and reusability
  - Enhanced maintainability and scalability
  - Better separation of concerns between different application features

- **Code Organization**
  - Moved route handlers to appropriate blueprint modules
  - Organized templates and static files by feature
  - Improved import structure and dependency management
  - Enhanced code readability and maintainability

### Removed
- **Old Monolithic App**
  - Removed `app_old.py` file (181KB, 4498 lines)
  - Eliminated monolithic application structure
  - Cleaned up legacy code and unused components
  - Streamlined codebase for better maintainability

### Fixed
- **Refactor-Related Issues**
  - Fixed email function calls to use proper mail instance
  - Resolved URL routing issues in templates
  - Fixed template filter registration
  - Corrected blueprint endpoint references
  - Resolved configuration loading issues

- **Test Suite Improvements**
  - Fixed backup verification to use correct table names
  - Enhanced email functionality tests with better data creation
  - Improved language picker configuration testing
  - Resolved test warnings and improved test reliability

### Technical Improvements
- **Architecture Enhancement**
  - Implemented proper Flask blueprint structure
  - Enhanced application scalability and maintainability
  - Improved code organization and readability
  - Better separation of concerns across modules

- **Testing Enhancements**
  - Added new test categories for refactored components
  - Enhanced test coverage and validation
  - Improved test reliability and consistency
  - Better integration with management script

## [1.8.0] - 2025-01-XX

### Added
- **Slovak Language Support**
  - Added Slovak (sk) as third supported language
  - Updated language picker to support 3 languages (EN, CS, SK)
  - Added Slovak translations for key interface elements
  - Created `test_slovak_language.py` for language testing
  - Updated configuration to include Slovak in supported locales

- **Enhanced Housekeeping System**
  - Added multiple photo uploads per housekeeping task
  - Implemented bulk operations for housekeeping tasks
  - Added amenity-housekeeper assignment system
  - Created housekeeping task detail views
  - Added photo management interface
  - Implemented task status workflow with restrictions
  - Added pay calculation system for completed tasks

- **User Date Format Preferences**
  - Added user-specific date format settings
  - Implemented 5 different date format options
  - Added date format conversion utilities
  - Created admin interface for date format management
  - Added Jinja2 filter for date formatting

- **Amenity Management System**
  - Created amenity management interface
  - Added amenity-housekeeper assignments
  - Implemented amenity-based task filtering
  - Added amenity creation and editing functionality

- **Enhanced Calendar System**
  - Added multi-calendar management
  - Implemented calendar event filtering
  - Enhanced Airbnb calendar sync
  - Added calendar statistics and analytics

- **User Management Improvements**
  - Added soft delete functionality for users
  - Implemented user retention management
  - Enhanced role-based access control
  - Added user data integrity preservation

### Changed
- **Terminology Updates**
  - Renamed "Trip" to "Accommodation" throughout the application
  - Updated all user-facing text to use "Ubytovanie" (Czech) and "Ubytovanie" (Slovak)
  - Maintained database model names for backward compatibility

- **Translation Improvements**
  - Fixed multi-line string formatting in translation files
  - Added missing translations for key interface elements
  - Improved translation consistency across languages
  - Enhanced translation file structure for easier maintenance

- **UI/UX Enhancements**
  - Improved housekeeping task interface
  - Enhanced bulk operation buttons and layout
  - Updated action button sizing for better usability
  - Improved photo upload interface

### Fixed
- **Date Formatting Issues**
  - Fixed date format string conversion from PHP/JS to Python strftime
  - Resolved calendar display issues with raw format strings
  - Fixed date formatting in various templates and APIs

- **Translation Issues**
  - Fixed undefined `moment` variable in Jinja2 templates
  - Resolved missing translation strings
  - Fixed translation compilation errors

- **Housekeeping System**
  - Fixed task creation when no default housekeeper is assigned
  - Resolved bulk update route registration issues
  - Fixed photo upload validation and storage

- **General Bug Fixes**
  - Fixed HTML structure issues in templates
  - Resolved database constraint issues
  - Fixed email template rendering issues

### Technical Improvements
- **Database Migrations**
  - Added migration 1.8.0 for default housekeeper pay
  - Enhanced migration system with better error handling
  - Improved migration rollback functionality

- **Testing Enhancements**
  - Added comprehensive test coverage for new features
  - Created specialized test files for language support
  - Enhanced system integration testing
  - Added housekeeping system testing

- **Code Quality**
  - Improved code organization and structure
  - Enhanced error handling and logging
  - Better separation of concerns
  - Improved documentation and comments

## [1.7.0] - 2025-01-XX

### Added
- **User Date Format System**
  - User-specific date format preferences
  - Date format conversion utilities
  - Admin interface for date format management

### Changed
- Enhanced date display throughout the application
- Improved date formatting consistency

## [1.6.0] - 2025-01-XX

### Added
- **Housekeeping Photo System**
  - Multiple photos per housekeeping task
  - Photo upload and management interface
  - Photo validation and storage system

## [1.5.0] - 2025-01-XX

### Added
- **User Soft Delete**
  - Soft delete functionality for users
  - Data integrity preservation
  - User retention management

## [1.4.0] - 2025-01-XX

### Added
- **Amenity-Housekeeper System**
  - Amenity management interface
  - Housekeeper assignments to amenities
  - Task assignment based on amenities

## [1.3.0] - 2025-01-XX

### Added
- **Calendar System**
  - Multi-calendar management
  - Calendar event handling
  - Calendar integration features

## [1.2.0] - 2025-01-XX

### Added
- **Amenity System**
  - Basic amenity management
  - Property amenity tracking
  - Amenity database structure

## [1.1.0] - 2025-01-XX

### Added
- **Performance Indexes**
  - Database performance optimization
  - Query optimization indexes
  - Foreign key optimizations

## [1.0.0] - 2025-01-XX

### Added
- **Initial Release**
  - Core guest registration system
  - User management and authentication
  - Trip/accommodation management
  - Registration workflow
  - Email notifications
  - PDF invoice generation
  - Multi-language support (English, Czech)
  - Admin dashboard
  - Data export functionality
  - Backup system
  - Migration system
  - Universal management script

### Features
- Complete guest registration workflow
- Document upload and management
- GDPR compliance features
- Role-based access control
- Comprehensive admin interface
- Email template system
- File management system
- Database migration system
- Backup and restore functionality
- Testing framework

## Migration History

### Version 1.8.0
- Added default housekeeper pay settings
- Enhanced pay calculation system

### Version 1.7.0
- Added user date format preferences
- Date format conversion utilities

### Version 1.6.0
- Added housekeeping photo system
- Photo upload and management

### Version 1.5.0
- Added user soft delete functionality
- Data integrity preservation

### Version 1.4.0
- Added amenity-housekeeper system
- Task assignment improvements

### Version 1.3.0
- Added calendar management system
- Multi-calendar support

### Version 1.2.0
- Added amenity management system
- Property amenity tracking

### Version 1.1.0
- Added performance optimization indexes
- Database query improvements

### Version 1.0.0
- Initial database schema
- Core system tables and relationships

## Breaking Changes

### Version 1.8.0
- None

### Version 1.7.0
- None

### Version 1.6.0
- None

### Version 1.5.0
- None

### Version 1.4.0
- None

### Version 1.3.0
- None

### Version 1.2.0
- None

### Version 1.1.0
- None

### Version 1.0.0
- Initial release

## Deprecations

### Version 1.8.0
- None

### Version 1.7.0
- None

### Version 1.6.0
- None

### Version 1.5.0
- None

### Version 1.4.0
- None

### Version 1.3.0
- None

### Version 1.2.0
- None

### Version 1.1.0
- None

### Version 1.0.0
- Initial release

## Security Updates

### Version 1.8.0
- Enhanced file upload validation
- Improved access control for housekeeping features
- Better session management

### Version 1.7.0
- Enhanced user data protection
- Improved date format validation

### Version 1.6.0
- Secure photo upload system
- File type validation improvements

### Version 1.5.0
- Enhanced user data integrity
- Improved soft delete security

### Version 1.4.0
- Enhanced amenity access control
- Improved task assignment security

### Version 1.3.0
- Enhanced calendar access control
- Improved event handling security

### Version 1.2.0
- Enhanced amenity management security
- Improved property access control

### Version 1.1.0
- Database security improvements
- Query optimization for security

### Version 1.0.0
- Initial security implementation
- GDPR compliance features
- Secure file uploads
- Role-based access control

## Performance Improvements

### Version 1.8.0
- Optimized bulk operations
- Enhanced photo upload performance
- Improved language switching

### Version 1.7.0
- Optimized date formatting
- Enhanced template rendering

### Version 1.6.0
- Optimized photo upload system
- Enhanced file management

### Version 1.5.0
- Optimized user management
- Enhanced data retrieval

### Version 1.4.0
- Optimized amenity system
- Enhanced task assignment

### Version 1.3.0
- Optimized calendar system
- Enhanced event handling

### Version 1.2.0
- Optimized amenity management
- Enhanced property tracking

### Version 1.1.0
- Database performance optimization
- Query performance improvements

### Version 1.0.0
- Initial performance implementation
- Database optimization
- Query optimization

## Known Issues

### Version 1.8.0
- None reported

### Version 1.7.0
- None reported

### Version 1.6.0
- None reported

### Version 1.5.0
- None reported

### Version 1.4.0
- None reported

### Version 1.3.0
- None reported

### Version 1.2.0
- None reported

### Version 1.1.0
- None reported

### Version 1.0.0
- None reported

## Installation Notes

### Version 1.8.0
- Requires database migration to version 1.8.0
- New environment variables for housekeeping features
- Updated translation files for Slovak support

### Version 1.7.0
- Requires database migration to version 1.7.0
- New user date format preferences

### Version 1.6.0
- Requires database migration to version 1.6.0
- New photo upload directories

### Version 1.5.0
- Requires database migration to version 1.5.0
- Enhanced user management

### Version 1.4.0
- Requires database migration to version 1.4.0
- New amenity system

### Version 1.3.0
- Requires database migration to version 1.3.0
- New calendar system

### Version 1.2.0
- Requires database migration to version 1.2.0
- New amenity management

### Version 1.1.0
- Requires database migration to version 1.1.0
- Performance improvements

### Version 1.0.0
- Initial installation
- Complete system setup required

## Upgrade Guide

### From 1.7.0 to 1.8.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Update environment variables for new features
4. Compile translations: `pybabel compile -d translations`
5. Test the new features

### From 1.6.0 to 1.7.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Test date format features

### From 1.5.0 to 1.6.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Create photo upload directories
4. Test photo upload features

### From 1.4.0 to 1.5.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Test user management features

### From 1.3.0 to 1.4.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Test amenity system

### From 1.2.0 to 1.3.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Test calendar system

### From 1.1.0 to 1.2.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Test amenity management

### From 1.0.0 to 1.1.0
1. Backup your database
2. Run database migrations: `python manage.py migrate migrate`
3. Test performance improvements

## Support

For issues and questions:
- Check the documentation in the `docs/` directory
- Review the troubleshooting sections
- Test with the provided test scripts
- Contact support with detailed error information

---

**Maintained by**: Development Team  
**Last Updated**: January 2025  
**Current Version**: 1.8.0 