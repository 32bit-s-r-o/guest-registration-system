# Backup System Documentation

[← Back to Documentation Index](../docs/README.md)

## Overview

The Guest Registration System includes a comprehensive backup system that provides both system-wide backups and monthly guest registration backups. The system ensures data safety with automated backup creation, secure storage, and easy restoration capabilities.

## Quick Start

```bash
# Create system backup (admin only)
python manage.py backup

# Access backup via web interface
# Admin → Backup → System Backup

# Monthly guest backup API
curl "http://localhost:5000/api/backup/guests?year=2025&month=6"
```

## Current System Status

- **Backup System**: ✅ Fully Functional
- **System Backup**: ✅ Available (ZIP download)
- **Monthly Backup API**: ✅ Available (CSV/JSON)
- **Guest Photo Exclusion**: ✅ Implemented
- **Access Control**: ✅ Admin-only protection

## Backup Types

### 1. System Backup

**Purpose**: Complete system backup including database and uploads
**Access**: Admin-only via web interface
**Format**: ZIP file download
**Contents**: Database dump + uploads (excluding guest photos)

**Features:**
- Full database dump using `pg_dump`
- Uploads directory backup (excluding guest photos)
- ZIP compression for easy download
- Automatic cleanup of temporary files
- Secure access control

### 2. Monthly Guest Backup

**Purpose**: Monthly guest registration data backup
**Access**: Admin-only via API
**Format**: CSV or JSON
**Contents**: Guest registrations for specific month/year

**Features:**
- Monthly guest registration data
- Multiple export formats (CSV/JSON)
- Language-specific data
- No guest photos included
- API-based access

## Backup Commands

### System Backup

```bash
# Via management script
python manage.py backup

# Via web interface
# Admin → Backup → System Backup
```

### Monthly Backup API

```bash
# Get current month backup
curl "http://localhost:5000/api/backup/guests?year=2025&month=6"

# Get specific month backup
curl "http://localhost:5000/api/backup/guests?year=2024&month=12"

# Get JSON format
curl "http://localhost:5000/api/backup/guests?year=2025&month=6&format=json"
```

## Web Interface

### System Backup Page

**URL**: `/admin/backup`

**Features:**
- One-click system backup creation
- ZIP file download
- Progress indication
- Error handling

### Monthly Backup Interface

**URL**: `/admin/backup` (same page)

**Features:**
- Year/month selection
- Format selection (CSV/JSON)
- Download buttons
- Real-time API testing

## API Endpoints

### Monthly Guest Backup API

**Endpoint**: `GET /api/backup/guests`

**Parameters:**
- `year` (required): Year for backup (e.g., 2025)
- `month` (required): Month for backup (1-12)
- `format` (optional): Export format (`csv` or `json`, default: `csv`)

**Response:**
- **CSV**: File download with guest data
- **JSON**: JSON response with guest data

**Example Response (JSON):**
```json
[
  {
    "id": 1,
    "registration_id": 40,
    "first_name": "John",
    "last_name": "Doe",
    "age_category": "adult",
    "document_type": "passport",
    "document_number": "ABC123456",
    "gdpr_consent": true,
    "created_at": "2025-06-23 14:30:00",
    "trip_title": "Summer Vacation 2025",
    "registration_email": "john.doe@example.com",
    "registration_language": "en"
  }
]
```

## Backup Content

### System Backup Contents

**Database Dump:**
- Complete PostgreSQL database dump
- All tables and data
- Indexes and constraints
- Stored procedures and functions

**Uploads Directory:**
- All uploaded files
- **Excludes**: Guest document photos (UUID-patterned files)
- Includes: Sample images, system files, other uploads

### Monthly Backup Contents

**Guest Data:**
- Guest registration information
- Personal details (name, age category)
- Document information (type, number)
- GDPR consent status
- Registration metadata (email, language, trip)

**Excluded Data:**
- Guest document photos
- Sensitive personal data
- System configuration files

## Security Features

### Access Control

- **Admin-only access**: All backup endpoints require admin authentication
- **Session validation**: Proper session checking
- **Role verification**: Admin role required

### Data Protection

- **Guest photo exclusion**: Automatic filtering of sensitive files
- **Secure file handling**: Temporary file cleanup
- **Error handling**: No sensitive data exposure in errors

### File Security

- **Temporary file cleanup**: Automatic removal after download
- **Secure file paths**: No path traversal vulnerabilities
- **Content validation**: File type and size validation

## Integration with Management Script

The backup system is fully integrated with the universal management script:

```bash
# Run backup tests
python manage.py backup

# Check system status (includes backup status)
python manage.py status

# Setup system (includes backup setup)
python manage.py setup
```

## Testing

### Backup System Tests

```bash
# Run comprehensive backup tests
python test_backup_functionality.py

# Test backup API
python test_backup_api.py

# Test via management script
python manage.py test
```

### Test Coverage

- ✅ System backup creation
- ✅ Monthly backup API
- ✅ Access control verification
- ✅ File format validation
- ✅ Error handling
- ✅ Guest photo exclusion

## Best Practices

### Regular Backups

1. **System Backups**
   ```bash
   # Weekly system backup
   python manage.py backup
   ```

2. **Monthly Guest Backups**
   ```bash
   # Monthly guest data backup
   curl "http://localhost:5000/api/backup/guests?year=2025&month=6"
   ```

### Backup Storage

1. **Local Storage**
   - Store backups in secure location
   - Implement retention policy
   - Regular backup verification

2. **Remote Storage**
   - Consider cloud backup solutions
   - Encrypt sensitive backups
   - Test restoration procedures

### Backup Verification

1. **Test Restoration**
   ```bash
   # Test database restoration
   psql -d test_db -f backup_file.sql
   ```

2. **Data Integrity**
   - Verify backup file integrity
   - Check backup content completeness
   - Validate backup format

## Troubleshooting

### Common Issues

1. **Backup Creation Fails**
   - Check database connectivity
   - Verify file permissions
   - Review error logs

2. **Access Denied**
   - Verify admin authentication
   - Check session validity
   - Confirm admin role

3. **File Download Issues**
   - Check file permissions
   - Verify temporary directory
   - Review browser settings

### Debug Commands

```bash
# Test backup functionality
python test_backup_functionality.py

# Check backup API
python test_backup_api.py

# Verify access control
python manage.py test
```

## Performance Considerations

### System Backup

- **Database Size**: Large databases may take time to dump
- **File Size**: Uploads directory can be large
- **Network**: Consider bandwidth for downloads

### Monthly Backup

- **Query Performance**: Optimized for monthly data retrieval
- **Memory Usage**: Minimal memory footprint
- **Response Time**: Fast API responses

## Related Documentation

- [Universal Management Script](management-script.md) - Management commands
- [Database Migrations](migrations.md) - Migration system
- [Testing Guide](testing.md) - Backup testing
- [Installation Guide](installation.md) - System setup

## Support

For backup issues:

1. Check access permissions
2. Verify database connectivity
3. Review error logs
4. Test backup functionality

## Version History

- **v1.0.0**: Initial backup system
- **v1.1.0**: Added monthly backup API
- **v1.2.0**: Enhanced security features
- **v1.3.0**: Web interface integration

---

[← Back to Documentation Index](../docs/README.md) 