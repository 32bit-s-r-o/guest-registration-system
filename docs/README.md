# Guest Registration System Documentation

Welcome to the comprehensive documentation for the Guest Registration System - a modern Flask-based web application for managing guest registrations, accommodations, invoices, and housekeeping tasks.

## 📚 Documentation Structure

### 🚀 Getting Started
- **[Installation Guide](installation.md)** - Setup and installation instructions
- **[Quick Start Guide](quick-start.md)** - Get up and running in minutes
- **[Configuration](configuration.md)** - Environment variables and settings

### 🛠️ System Management
- **[Universal Management Script](management-script.md)** - Complete guide to `manage.py`
- **[Database Migrations](migrations.md)** - Migration system and versioning
- **[Backup System](backup-system.md)** - Backup and restore functionality
- **[Testing Guide](testing.md)** - Comprehensive testing documentation
- **[Tag Management](tag-management.md)** - Git tag management and release procedures
- **[Docker Deployment](docker.md)** - Docker containerization and deployment

### 🔧 Development
- **[API Documentation](api.md)** - REST API endpoints and usage
- **[Database Schema](database-schema.md)** - Database models and relationships
- **[Translation System](translations.md)** - Multi-language support with Flask-Babel
- **[Email System](email-system.md)** - Email functionality and templates

### 📊 Features
- **[Guest Registration](guest-registration.md)** - Guest registration workflow
- **[Accommodation Management](accommodation-management.md)** - Creating and managing accommodations
- **[Invoice System](invoice-system.md)** - PDF generation and email sending
- **[Housekeeping](housekeeping.md)** - Housekeeping task management
- **[User Management](user-management.md)** - Admin and housekeeper roles
- **[Analytics & Reports](analytics.md)** - Data export and breakdowns

### 🔒 Security & Access Control
- **[Authentication](authentication.md)** - Login system and session management
- **[Role-Based Access](access-control.md)** - Admin and housekeeper permissions
- **[GDPR Compliance](gdpr.md)** - Data protection and privacy

### 🚀 Deployment
- **[Production Deployment](deployment.md)** - Production setup and configuration
- **[Docker Setup](docker.md)** - Containerized deployment
- **[Monitoring](monitoring.md)** - System monitoring and logging

## 🎯 System Overview

The Guest Registration System is a comprehensive web application built with:

- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with migration system
- **Frontend**: Bootstrap 5 with responsive design
- **Internationalization**: Flask-Babel with English, Czech, and Slovak support
- **PDF Generation**: ReportLab for invoice generation
- **Email**: SMTP integration with template support
- **File Management**: Secure file uploads with validation

### Key Features

✅ **Multi-language Support** - English, Czech, and Slovak interfaces  
✅ **Guest Registration** - Complete registration workflow with document uploads  
✅ **Accommodation Management** - Create and manage accommodation bookings  
✅ **Invoice System** - Generate and email PDF invoices  
✅ **Housekeeping System** - Complete task management for cleaning staff  
✅ **User Management** - Role-based access control with soft delete  
✅ **Data Export** - CSV and JSON export functionality  
✅ **Backup System** - Automated backup and restore  
✅ **Migration System** - Database versioning and rollbacks  
✅ **Universal Management** - Single command-line interface for all operations  
✅ **Date Format Customization** - User-specific date format preferences  
✅ **Photo Management** - Multiple photos per housekeeping task  
✅ **Amenity System** - Manage property amenities and assignments  
✅ **Calendar Integration** - Multi-calendar management with Airbnb sync  
✅ **Bulk Operations** - Bulk update housekeeping tasks  

## 🚀 Quick Commands

```bash
# Check system status
python manage.py status

# Run all tests
python manage.py test

# Apply database migrations
python manage.py migrate migrate

# Setup system from scratch
python manage.py setup

# Create backup
python manage.py backup

# Clean up system
python manage.py clean

# Test language support
python test_language_picker.py
python test_slovak_language.py
```

## 📊 Current System Status

- **Database Version**: 1.8.0 (Latest)
- **Applied Migrations**: 8
- **Pending Migrations**: 0
- **Flask Application**: ✅ Running
- **All Tests**: ✅ Passing
- **Management Script**: ✅ Fully Functional
- **Language Support**: ✅ English, Czech, Slovak
- **Housekeeping System**: ✅ Complete with photo uploads
- **Date Formatting**: ✅ User-customizable

## 🔗 Quick Links

- **[GitHub Repository](https://github.com/32bit-s-r-o/guest-registration-system)**
- **[Live Demo](https://your-demo-url.com)**
- **[Issue Tracker](https://github.com/32bit-s-r-o/guest-registration-system/issues)**
- **[Contributing Guide](contributing.md)**

## 📞 Support

For support and questions:
- **Documentation Issues**: Create an issue in the repository
- **Feature Requests**: Use the issue tracker
- **Bug Reports**: Include system information and error logs

---

**Last Updated**: January 2025  
**Version**: 1.8.0  
**Status**: Production Ready ✅ 