# Docker Deployment Guide

[← Back to Documentation Index](README.md)

## Overview

This guide covers Docker deployment for the Guest Registration System, including multi-platform support, production-ready configuration, and management commands.

## 🏗️ Architecture

The system consists of three main services:

1. **PostgreSQL** - Primary database
2. **Flask Application** - Main web application
3. **Nginx** - Reverse proxy and static file server

## 🐳 Docker Architecture

The system uses a multi-service Docker Compose setup:

### Services

1. **PostgreSQL Database** - Primary data storage
2. **Flask Application** - Main application with Gunicorn
3. **Nginx** - Reverse proxy and load balancer

### Multi-Platform Support

The Docker setup supports multiple platforms:
- `linux/amd64` - Intel/AMD x86_64 architecture (traditional servers, desktops)
- `linux/arm64` - ARM 64-bit (Apple Silicon, ARM servers)
- `linux/arm/v7` - ARM 32-bit (Raspberry Pi, ARM devices)
- `linux/arm/v6` - ARM 32-bit (older Raspberry Pi)
- `linux/386` - x86 32-bit (Intel/AMD 32-bit)
- `linux/ppc64le` - PowerPC 64-bit little-endian
- `linux/s390x` - IBM S390x (mainframe)
- `linux/riscv64` - RISC-V 64-bit

**Note**: `linux/amd64` is the same as x86_64 architecture and is the default platform.

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Docker Buildx (for multi-platform builds)

### 1. Build and Start

```bash
# Build for current platform (defaults to x86_64)
python manage.py docker build

# Build specifically for x86_64
python manage.py docker build linux/amd64

# Start all services
python manage.py docker up

# Check status
python manage.py docker status
```

### 2. Access the Application

- **Application**: http://localhost:8000
- **Nginx Proxy**: http://localhost:80
- **Database**: localhost:5432

## 🔧 Docker Management Commands

### Using manage.py

```bash
# List all Docker operations
python manage.py docker

# Build Docker image (defaults to x86_64)
python manage.py docker build

# Build for specific platform
python manage.py docker build linux/amd64 guest-registration:v1.8.0
python manage.py docker build linux/arm64 guest-registration:v1.8.0

# Multi-platform build (includes x86_64)
python manage.py docker multi-build linux/amd64,linux/arm64

# Build for ALL processor architectures
python manage.py docker all-platforms guest-registration:v1.8.0
python manage.py docker all-platforms guest-registration:v1.8.0 true  # Push to registry

# Start services
python manage.py docker up

# Stop services
python manage.py docker down

# Show logs
python manage.py docker logs app

# Check status
python manage.py docker status

# Clean resources
python manage.py docker clean

# Push to registry
python manage.py docker push guest-registration:v1.8.0
```

### Direct Docker Commands

```bash
# Build for x86_64
docker buildx build --platform linux/amd64 --tag guest-registration:latest .

# Build for ARM64
docker buildx build --platform linux/arm64 --tag guest-registration:latest .

# Multi-platform build (includes x86_64)
docker buildx build --platform linux/amd64,linux/arm64 --tag guest-registration:latest .

# Build for ALL platforms
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7,linux/arm/v6,linux/386,linux/ppc64le,linux/s390x,linux/riscv64 --tag guest-registration:latest .

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Check status
docker-compose ps
```

## 📁 File Structure

```
├── Dockerfile                 # Multi-stage Dockerfile
├── docker-compose.yml         # Service orchestration
├── nginx.conf                 # Nginx configuration
├── .dockerignore             # Build context exclusions
├── config.env.production     # Production environment template
└── docs/
    └── docker.md             # This documentation
```

## 🏗️ Dockerfile Details

### Multi-Stage Build

```dockerfile
# Build stage
FROM --platform=$BUILDPLATFORM python:3.11-slim as builder
# Install dependencies and create virtual environment

# Production stage
FROM --platform=$TARGETPLATFORM python:3.11-slim
# Copy virtual environment and run application
```

### Features

- **Multi-platform support** with buildx (x86_64, ARM64, ARMv7, ARMv6, x86_32, PowerPC, S390x, RISC-V)
- **Non-root user** for security
- **Health checks** for monitoring
- **Optimized layers** for faster builds
- **Production-ready** Gunicorn configuration

## 🔄 Docker Compose Configuration

### Services Overview

```yaml
services:
  postgres:     # PostgreSQL database
  app:          # Flask application (multi-platform)
  nginx:        # Reverse proxy
```

### Platform Support

```yaml
app:
  build:
    platforms:
      - linux/amd64   # x86_64 architecture (default)
      - linux/arm64   # ARM 64-bit
      - linux/arm/v7  # ARM 32-bit
      - linux/arm/v6  # ARM 32-bit (older)
      - linux/386     # x86 32-bit
      - linux/ppc64le # PowerPC 64-bit
      - linux/s390x   # IBM S390x
      - linux/riscv64 # RISC-V 64-bit
```

### Key Features

- **Health checks** for all services
- **Volume persistence** for data
- **Network isolation** between services
- **Environment variable** configuration
- **Restart policies** for reliability

## 🌐 Nginx Configuration

### Features

- **Reverse proxy** to Flask application
- **Static file serving** with caching
- **Gzip compression** for performance
- **Rate limiting** for security
- **Security headers** for protection
- **SSL/TLS support** (commented)

### Configuration Highlights

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
```

## 🔧 Production Configuration

### Environment Variables

Copy `config.env.production` to `.env.production` and configure:

```bash
# Database
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://postgres:password@postgres:5432/guest_registration

# Flask
SECRET_KEY=your_very_secure_secret_key
FLASK_ENV=production

# Email
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password

# Security
ENABLE_RATE_LIMITING=true
ENABLE_CSRF_PROTECTION=true
```

### Gunicorn Configuration

```bash
# Workers
GUNICORN_WORKERS=4

# Timeout
GUNICORN_TIMEOUT=120

# Max requests
GUNICORN_MAX_REQUESTS=1000
```

## 🔒 Security Considerations

### Container Security

- **Non-root user** execution
- **Minimal base images** (slim variants)
- **Multi-stage builds** to reduce attack surface
- **Health checks** for monitoring

### Network Security

- **Internal network** for service communication
- **Exposed ports** only where necessary
- **Reverse proxy** for external access
- **Rate limiting** for API protection

### Data Security

- **Volume mounts** for persistent data
- **Environment variables** for secrets
- **Database isolation** in separate container
- **Backup volumes** for data protection

## 📊 Monitoring and Health Checks

### Health Check Endpoints

```bash
# Application health
curl http://localhost:8000/health

# Docker health checks
docker-compose ps
```

### Health Check Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "1.8.0",
  "database": "connected"
}
```

## 🚀 Deployment Scenarios

### Development

```bash
# Quick development setup (x86_64)
python manage.py docker build
python manage.py docker up
```

### Production

```bash
# Production build (multi-platform including x86_64)
python manage.py docker multi-build linux/amd64,linux/arm64

# Production deployment
docker-compose -f docker-compose.yml --env-file .env.production up -d
```

### CI/CD Pipeline

```yaml
# Example GitHub Actions
- name: Build Docker image
  run: python manage.py docker multi-build

- name: Push to registry
  run: python manage.py docker push ${{ env.IMAGE_TAG }}

- name: Deploy
  run: docker-compose pull && docker-compose up -d
```

## 🔧 Troubleshooting

### Common Issues

1. **Build fails on ARM**
   ```bash
   # Enable buildx
   docker buildx create --use
   ```

2. **Database connection fails**
   ```bash
   # Check service status
   python manage.py docker status
   
   # Check logs
   python manage.py docker logs postgres
   ```

3. **Permission issues**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 ./uploads
   ```

4. **Port conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :80
   
   # Change ports in docker-compose.yml
   ```

### Debug Commands

```bash
# Enter container
docker-compose exec app bash

# View logs
docker-compose logs -f

# Check resource usage
docker stats

# Inspect container
docker inspect guest_registration_app
```

## 📈 Performance Optimization

### Build Optimization

- **Multi-stage builds** reduce image size
- **Layer caching** speeds up rebuilds
- **Dockerignore** excludes unnecessary files
- **Alpine base** for smaller images

### Runtime Optimization

- **Gunicorn workers** based on CPU cores
- **Nginx caching** for static files
- **Gzip compression** for responses

### Resource Limits

```yaml
# In docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

## 🔄 Backup and Recovery

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres guest_registration > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres guest_registration < backup.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v guest_registration_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v guest_registration_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 🌍 Multi-Platform Deployment

### Supported Platforms

- **linux/amd64** - Intel/AMD x86_64 architecture (traditional servers, desktops)
- **linux/arm64** - ARM 64-bit (Apple Silicon, ARM servers)
- **linux/arm/v7** - ARM 32-bit (Raspberry Pi, ARM devices)
- **linux/arm/v6** - ARM 32-bit (older Raspberry Pi)
- **linux/386** - x86 32-bit (Intel/AMD 32-bit)
- **linux/ppc64le** - PowerPC 64-bit little-endian
- **linux/s390x** - IBM S390x (mainframe)
- **linux/riscv64** - RISC-V 64-bit

### Platform-Specific Builds

```bash
# Build for x86_64
python manage.py docker build linux/amd64 guest-registration:x86_64

# Build for ARM64
python manage.py docker build linux/arm64 guest-registration:arm64

# Build for ALL platforms
python manage.py docker all-platforms guest-registration:universal

# Build for multiple platforms (includes x86_64)
python manage.py docker multi-build linux/amd64,linux/arm64,linux/arm/v7
```

### Registry Push

```bash
# Tag for registry
docker tag guest-registration:latest your-registry.com/guest-registration:v1.8.0

# Push to registry
python manage.py docker push your-registry.com/guest-registration:v1.8.0
```

## 📚 Related Documentation

- [Installation Guide](installation.md) - System setup
- [Configuration](configuration.md) - Environment configuration
- [Production Deployment](deployment.md) - Production setup
- [Backup System](backup-system.md) - Backup procedures
- [Testing Guide](testing.md) - Testing procedures

## 🆘 Support

For Docker-related issues:

1. Check service status: `python manage.py docker status`
2. View logs: `python manage.py docker logs`
3. Check health: `curl http://localhost:8000/health`
4. Review configuration files
5. Check Docker documentation

---

**Last Updated**: January 2025  
**Docker Version**: 20.10+  
**Compose Version**: 2.0+  
**Supported Platforms**: x86_64, ARM64, ARMv7

[← Back to Documentation Index](README.md) 