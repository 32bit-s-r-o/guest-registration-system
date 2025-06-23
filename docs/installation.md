# Installation Guide

[← Back to Documentation Index](README.md)

## Overview

This guide provides step-by-step instructions for installing and setting up the Guest Registration System on your local machine or production server.

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.7 or higher
- **PostgreSQL**: 12 or higher
- **Memory**: Minimum 2GB RAM
- **Storage**: Minimum 1GB free space

### Required Software

1. **Python 3.7+**
   ```bash
   # Check Python version
   python --version
   
   # Install Python (Ubuntu/Debian)
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   
   # Install Python (macOS)
   brew install python3
   
   # Install Python (Windows)
   # Download from https://python.org
   ```

2. **PostgreSQL 12+**
   ```bash
   # Install PostgreSQL (Ubuntu/Debian)
   sudo apt install postgresql postgresql-contrib
   
   # Install PostgreSQL (macOS)
   brew install postgresql
   
   # Install PostgreSQL (Windows)
   # Download from https://postgresql.org
   ```

3. **Git**
   ```bash
   # Install Git (Ubuntu/Debian)
   sudo apt install git
   
   # Install Git (macOS)
   brew install git
   
   # Install Git (Windows)
   # Download from https://git-scm.com
   ```

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/32bit-s-r-o/guest-registration-system.git
cd guest-registration-system
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### 4. Set Up Database

```bash
# Create PostgreSQL database
sudo -u postgres createdb airbnb_guests

# Create database user (optional)
sudo -u postgres createuser --interactive airbnb_user
```

### 5. Configure Environment

```bash
# Copy environment template
cp config.env.example config.env

# Edit configuration file
nano config.env
```

**Required Environment Variables:**

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/airbnb_guests

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Table Prefix (optional)
TABLE_PREFIX=guest_reg_

# Language Picker (optional)
LANGUAGE_PICKER_ENABLED=true
```

### 6. Initialize the System

```bash
# Run system setup
python manage.py setup

# This will:
# - Create necessary directories
# - Apply database migrations
# - Create seed data
# - Run system tests
# - Create initial backup
```

### 7. Create Admin User

```bash
# Create admin user via web interface
# 1. Start the application
python app.py

# 2. Access http://localhost:5000/admin/login
# 3. Use default credentials or create new admin
```

## Quick Installation Script

For automated installation, use the provided setup script:

```bash
# Run setup script
python setup.py

# This script will:
# - Check prerequisites
# - Install dependencies
# - Set up database
# - Configure environment
# - Initialize system
```

## Development Setup

### Additional Development Tools

```bash
# Install development dependencies
pip install pytest pytest-cov black flake8

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Development Environment Variables

```bash
# Development configuration
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=postgresql://localhost/airbnb_guests_dev
```

## Production Setup

### Production Environment Variables

```bash
# Production configuration
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://prod_user:prod_pass@prod_host/airbnb_guests_prod
SECRET_KEY=your-production-secret-key
```

### Production Server Setup

```bash
# Install production server
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/airbnb-guest.service
```

**Systemd Service Configuration:**

```ini
[Unit]
Description=Guest Registration System
After=network.target

[Service]
User=airbnb
WorkingDirectory=/path/to/guest-registration-system
Environment=PATH=/path/to/guest-registration-system/venv/bin
ExecStart=/path/to/guest-registration-system/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/guest-registration-system/static;
    }
}
```

## Docker Setup

### Docker Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Docker Compose Configuration

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db/airbnb_guests
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=airbnb_guests
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Docker Commands

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Verification

### System Health Check

```bash
# Check system status
python manage.py status

# Expected output:
# ✅ Flask application is running
# 📊 Database Version: 000001
# 📊 Applied Migrations: 2
# 📊 Pending Migrations: 0
```

### Test System

```bash
# Run all tests
python manage.py test

# Expected output:
# Tests passed: 9/9
# ✅ All management script tests passed!
```

### Access Application

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Access the application:**
   - Main site: http://localhost:5000
   - Admin panel: http://localhost:5000/admin/login

3. **Default credentials:**
   - Username: admin
   - Password: admin123

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check database connection
   psql -h localhost -U postgres -d airbnb_guests
   ```

2. **Python Package Issues**
   ```bash
   # Reinstall packages
   pip install --force-reinstall -r requirements.txt
   
   # Check Python version
   python --version
   ```

3. **Permission Issues**
   ```bash
   # Fix upload directory permissions
   sudo chown -R $USER:$USER uploads/
   chmod 755 uploads/
   ```

4. **Port Already in Use**
   ```bash
   # Check port usage
   lsof -i :5000
   
   # Kill process
   kill -9 <PID>
   ```

### Debug Mode

```bash
# Enable debug mode
export FLASK_DEBUG=True
export FLASK_ENV=development

# Run with debug
python app.py
```

## Security Considerations

### Production Security

1. **Change Default Passwords**
   - Update admin password
   - Use strong database passwords
   - Secure secret keys

2. **SSL/TLS Configuration**
   - Enable HTTPS
   - Configure SSL certificates
   - Use secure headers

3. **Database Security**
   - Use dedicated database user
   - Restrict database access
   - Regular backups

4. **File Permissions**
   - Secure upload directory
   - Restrict file access
   - Validate file uploads

## Support

For installation issues:

1. Check prerequisites
2. Review error logs
3. Verify configuration
4. Test connectivity

## Related Documentation

- [Quick Start Guide](quick-start.md) - Get started quickly
- [Configuration Guide](configuration.md) - Detailed configuration
- [Universal Management Script](management-script.md) - System management
- [Deployment Guide](deployment.md) - Production deployment

---

[← Back to Documentation Index](README.md) 