# Release Notes

## Version 1.8.0 - January 2025

### 🎉 Major New Features

#### 🌍 Slovak Language Support
We're excited to announce the addition of Slovak as our third supported language! The system now supports:
- **English** 🇬🇧 - Default language
- **Czech** 🇨🇿 - Secondary language  
- **Slovak** 🇸🇰 - New third language

**What's new:**
- Complete Slovak translation coverage
- Language picker updated to support 3 languages
- All interface elements translated to Slovak
- Comprehensive testing for language switching

#### 🧹 Enhanced Housekeeping System
The housekeeping system has been completely overhauled with powerful new features:

**Photo Management:**
- Upload multiple photos per housekeeping task
- Support for JPG, PNG, and GIF formats
- Maximum file size: 16MB per photo
- Secure photo storage and management

**Bulk Operations:**
- Update multiple tasks simultaneously
- Bulk status changes
- Bulk reassignment to different housekeepers
- Bulk deletion with confirmation

**Task Management:**
- Enhanced task detail views
- Improved status workflow
- Better task assignment system
- Pay calculation for completed tasks

#### 📅 User Date Format Preferences
Users can now customize how dates are displayed throughout the system:

**Available Formats:**
- `d.m.Y` - 26.3.2025 (Day.Month.Year)
- `Y-m-d` - 2025-03-26 (Year-Month-Day)
- `d/m/Y` - 26/03/2025 (Day/Month/Year)
- `m/d/Y` - 03/26/2025 (Month/Day/Year)
- `d.m.y` - 26.3.25 (Day.Month.Year short)

**Features:**
- Personal date format settings
- Automatic format conversion
- Admin interface for management
- Consistent date display across the system

#### 🏠 Amenity Management System
New comprehensive amenity management for properties:

**Features:**
- Create and manage property amenities
- Assign housekeepers to specific amenities
- Filter housekeeping tasks by amenity
- Track amenity-specific performance

**Amenity Types:**
- Cleaning services
- Maintenance tasks
- Specialized services
- Custom amenities

#### 📊 Enhanced Calendar System
Improved calendar management with new capabilities:

**Features:**
- Multi-calendar management
- Enhanced Airbnb calendar sync
- Calendar event filtering
- Calendar statistics and analytics
- Better event handling

#### 👥 User Management Improvements
Enhanced user management with data integrity features:

**New Features:**
- Soft delete functionality for users
- User data retention management
- Enhanced role-based access control
- Better user data protection

### 🔄 Terminology Updates

We've updated the terminology throughout the application for better clarity:

**Changes:**
- "Trip" → "Accommodation" (English)
- "Výlet" → "Ubytovanie" (Czech)
- "Výlet" → "Ubytovanie" (Slovak)

**Note:** Database model names remain unchanged for backward compatibility.

### 🐛 Bug Fixes

#### Date Formatting
- Fixed date format string conversion issues
- Resolved calendar display problems
- Improved date formatting consistency

#### Translation System
- Fixed multi-line string formatting
- Resolved missing translation strings
- Improved translation compilation

#### Housekeeping System
- Fixed task creation when no default housekeeper is assigned
- Resolved bulk update route registration
- Fixed photo upload validation

#### General Improvements
- Fixed HTML structure issues
- Resolved database constraint problems
- Improved email template rendering

### 🚀 Performance Improvements

- Optimized bulk operations for better speed
- Enhanced photo upload performance
- Improved language switching responsiveness
- Better database query optimization

### 🔒 Security Enhancements

- Enhanced file upload validation
- Improved access control for housekeeping features
- Better session management
- Enhanced user data protection

### 📚 Documentation Updates

- Complete documentation overhaul
- New housekeeping system guide
- Updated configuration documentation
- Enhanced testing documentation
- Comprehensive migration history

### 🧪 Testing Improvements

- Added comprehensive test coverage for new features
- Created specialized test files for language support
- Enhanced system integration testing
- Added housekeeping system testing

## Installation & Upgrade

### New Installation
1. Follow the installation guide in `docs/installation.md`
2. Run initial setup: `python manage.py setup`
3. Configure environment variables
4. Test the system: `python manage.py test`

### Upgrading from Previous Versions
1. **Backup your database**
2. Run migrations: `python manage.py migrate migrate`
3. Update environment variables for new features
4. Compile translations: `pybabel compile -d translations`
5. Test new features

### New Environment Variables
```bash
# Housekeeping settings
DEFAULT_HOUSEKEEPER_PAY=25.00
HOUSEKEEPER_CURRENCY=EUR
ENABLE_HOUSEKEEPING_PHOTOS=true
MAX_HOUSEKEEPING_PHOTO_SIZE=16777216
ENABLE_BULK_HOUSEKEEPING_OPERATIONS=true

# Amenity system
ENABLE_AMENITY_SYSTEM=true
ENABLE_AMENITY_HOUSEKEEPER_ASSIGNMENTS=true
```

## Breaking Changes

**None** - This release maintains full backward compatibility.

## Known Issues

**None reported** - All known issues have been resolved.

## Support

For support and questions:
- Check the documentation in the `docs/` directory
- Review the troubleshooting sections
- Test with the provided test scripts
- Contact support with detailed error information

## What's Next

We're already working on future improvements:
- Enhanced reporting and analytics
- Mobile app development
- Advanced automation features
- Integration with additional booking platforms

---

**Release Date**: January 2025  
**Version**: 1.8.0  
**Status**: Production Ready ✅

Thank you for using the Guest Registration System! 