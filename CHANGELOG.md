# Changelog

All notable changes to the Guest Registration System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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