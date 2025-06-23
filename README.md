# Guest Registration System

A comprehensive Flask-based web application for managing guest registrations, trips, invoices, and housekeeping tasks with multi-language support, PDF generation, and automated backup systems.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/32bit-s-r-o/guest-registration-system.git
cd guest-registration-system

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb airbnb_guests

# Configure environment
cp config.env.example config.env
# Edit config.env with your settings

# Initialize system
python manage.py setup

# Start the application
python app.py
```

### Flask App Parameters

The application supports various command-line parameters for flexible deployment:

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

**Common Usage Examples:**
```bash
# Development with auto-reload
python app.py --debug --reload --port 5001

# Production server (accessible from network)
python app.py --host 0.0.0.0 --port 80 --no-debug --threaded

# HTTPS with self-signed certificate
python app.py --ssl-context adhoc --port 443

# Custom port for testing
python app.py --port 8080
```

**Access the application:**
- Main site: http://localhost:5000
- Admin panel: http://localhost:5000/admin/login
- Default admin: `admin` / `admin123`

## 📚 Documentation

**📖 [Complete Documentation](docs/README.md)** - Full system documentation with guides, API reference, and examples.

### Quick Links

- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Quick Start Guide](docs/quick-start.md)** - Get running in 5 minutes
- **[Configuration Guide](docs/configuration.md)** - Environment and system settings
- **[Universal Management Script](docs/management-script.md)** - Complete system management
- **[Database Migrations](docs/migrations.md)** - Migration system and versioning
- **[Backup System](docs/backup-system.md)** - Backup and restore functionality
- **[Testing Guide](docs/testing.md)** - Comprehensive testing documentation

## 🎯 Features

### ✅ Core Functionality
- **Multi-language Support** - English and Czech interfaces
- **Guest Registration** - Complete workflow with document uploads
- **Trip Management** - Create and manage accommodation trips
- **Invoice System** - Generate and email PDF invoices
- **Housekeeping** - Task management for cleaning staff
- **User Management** - Role-based access control (Admin/Housekeeper)

### ✅ Advanced Features
- **Data Export** - CSV and JSON export functionality
- **Backup System** - Automated backup and restore
- **Migration System** - Database versioning and rollbacks
- **Universal Management** - Single command-line interface for all operations
- **Email Integration** - SMTP support with template rendering
- **File Management** - Secure file uploads with validation

### ✅ System Management
- **Universal Management Script** - `python manage.py` for all operations
- **Comprehensive Testing** - 9/9 tests passing with full coverage
- **Production Ready** - Secure, scalable, and well-documented
- **Docker Support** - Containerized deployment options

## 🛠️ System Management

The system includes a universal management script (`manage.py`) that provides unified access to all operations:

```bash
# Check system status
python manage.py status

# Run all tests
python manage.py test

# Apply database migrations
python manage.py migrate migrate

# Create backup
python manage.py backup

# Setup system from scratch
python manage.py setup

# Clean up system
python manage.py clean

# Run all operations
python manage.py all
```

## 📊 Current System Status

- **Database Version**: 000001 (Latest)
- **Applied Migrations**: 2
- **Pending Migrations**: 0
- **Flask Application**: ✅ Running
- **All Tests**: ✅ Passing (9/9)
- **Management Script**: ✅ Fully Functional

## 🏗️ Architecture

### Technology Stack
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: PostgreSQL with migration system
- **Frontend**: Bootstrap 5 with responsive design
- **Internationalization**: Flask-Babel with English and Czech support
- **PDF Generation**: ReportLab for invoice generation
- **Email**: SMTP integration with template support
- **File Management**: Secure file uploads with validation

### System Components
- **Web Application** (`app.py`) - Main Flask application
- **Migration System** (`migrations.py`) - Database versioning
- **Version Management** (`version.py`) - App and DB versioning
- **Universal Management** (`manage.py`) - System management script
- **Test Suites** - Comprehensive testing coverage

## 🔧 Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://localhost/airbnb_guests
SECRET_KEY=your-secret-key-here

# Optional
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
TABLE_PREFIX=guest_reg_
LANGUAGE_PICKER_ENABLED=true
```

### Database Setup

```bash
# Create database
createdb airbnb_guests

# Apply migrations
python manage.py migrate migrate

# Create seed data
python manage.py seed
```

## 🧪 Testing

The system includes comprehensive testing with 9/9 tests passing:

```bash
# Run all tests
python manage.py test

# Run specific test suites
python test_backup_functionality.py
python test_migration_system.py
python system_test.py
python test_email_functionality.py
python test_csv_export.py
python test_language_picker.py
```

## 📦 Installation Options

### Standard Installation
```bash
git clone https://github.com/32bit-s-r-o/guest-registration-system.git
cd guest-registration-system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py setup
```

### Docker Installation
```bash
# Using Docker Compose
docker-compose up -d

# Or build manually
docker build -t guest-registration-system .
docker run -p 5000:5000 guest-registration-system
```

### Production Deployment
See [Deployment Guide](docs/deployment.md) for production setup instructions.

## 🔒 Security Features

- **Role-based Access Control** - Admin and Housekeeper roles
- **Session Management** - Secure session handling
- **File Upload Security** - Validation and secure storage
- **Database Security** - Parameterized queries and connection security
- **Email Security** - SMTP with TLS support
- **Backup Security** - Guest photo exclusion and access control

## 📈 Performance

- **Database Optimization** - Indexed queries and efficient schema
- **File Management** - Optimized upload handling
- **Caching** - Session and template caching
- **Backup Efficiency** - Incremental and selective backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [Complete Documentation](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/32bit-s-r-o/guest-registration-system/issues)
- **Questions**: Create an issue or check the documentation

## 🗺️ Roadmap

- [ ] Additional language support
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Payment gateway integration
- [ ] API rate limiting
- [ ] Advanced backup scheduling

---

**Status**: Production Ready ✅  
**Version**: 1.0.0  
**Last Updated**: June 23, 2025

For complete documentation, visit [docs/README.md](docs/README.md). 