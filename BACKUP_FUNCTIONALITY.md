# Backup Functionality Documentation

## Overview

The Guest Registration System now includes comprehensive backup functionality with two main features:

1. **System Backup** - Full system backup including database and uploads (excluding guest photos)
2. **Monthly Guest Backup API** - API endpoint to export guest registrations by month

## Features

### 1. System Backup (`/admin/backup`)

**Access:** Admin only  
**Method:** GET  
**Output:** ZIP file download

**What's included:**
- Complete PostgreSQL database dump
- All uploads (excluding guest document photos for GDPR compliance)
- Timestamped filename: `system_backup_YYYYMMDD_HHMMSS.zip`

**What's excluded:**
- Guest document photos (files matching pattern: `uuid_*.jpg/png`)
- Temporary files
- System logs

**Usage:**
1. Login as admin
2. Go to Admin Dashboard
3. Click "System Backup" button
4. Download will start automatically

### 2. Monthly Guest Backup API (`/api/backup/guests`)

**Access:** Admin only  
**Method:** GET  
**Output:** CSV (default) or JSON

**Parameters:**
- `year` (required): Year (e.g., 2024)
- `month` (required): Month (1-12)
- `format` (optional): `csv` or `json` (default: `csv`)

**Data included:**
- Guest ID, registration ID
- First name, last name
- Age category, document type, document number
- GDPR consent status
- Created date
- Trip title, registration email, registration language

**Data excluded:**
- Document photos (for GDPR compliance)
- Sensitive personal data beyond what's needed for records

**Usage Examples:**

```bash
# CSV export for June 2024
curl -H "Cookie: session=..." "http://localhost:5000/api/backup/guests?year=2024&month=6"

# JSON export for December 2024
curl -H "Cookie: session=..." "http://localhost:5000/api/backup/guests?year=2024&month=12&format=json"
```

## Security Features

### Access Control
- All backup endpoints require admin authentication
- Unauthenticated requests redirect to login page
- Session-based authentication required

### Data Protection
- Guest document photos are automatically excluded from backups
- GDPR-compliant data handling
- No sensitive personal data in monthly exports

## Technical Implementation

### System Backup Process
1. Parse database connection string
2. Execute `pg_dump` with table filtering
3. Copy uploads directory (excluding photos)
4. Create ZIP archive
5. Serve as download
6. Clean up temporary files

### Monthly Backup Process
1. Query guests by registration date range
2. Filter out photo data
3. Format as CSV or JSON
4. Return as file download or JSON response

## Testing

### Test Scripts
- `test_backup_api.py` - Tests API endpoints and access control
- `test_backup_functionality.py` - Comprehensive backup testing

### Test Coverage
- ✅ Access control (admin-only)
- ✅ Monthly guest backup API (CSV/JSON)
- ✅ System backup (ZIP download)
- ✅ Error handling
- ✅ Data integrity (no photos included)

## Configuration

### Database Requirements
- PostgreSQL database
- `pg_dump` utility must be available
- Proper database permissions

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
TABLE_PREFIX=guest_reg_
```

## Usage Recommendations

### Regular Backups
- **Daily:** System backup during low-traffic hours
- **Monthly:** Guest registration exports for compliance
- **Before updates:** System backup before major changes

### Storage
- Store backups in separate location/server
- Keep 7 daily backups + 4 weekly backups
- Monitor backup file sizes for anomalies

### Automation
```bash
# Example cron job for daily backup
0 2 * * * /path/to/backup_script.sh

# Example backup script
#!/bin/bash
export PGPASSWORD="your_password"
pg_dump -h localhost -U postgres -d your_db \
  -t guest_reg_admin -t guest_reg_trip \
  -t guest_reg_registration -t guest_reg_guest \
  --no-owner --no-privileges \
  -f /backups/guest_reg_$(date +%Y%m%d_%H%M%S).sql
```

## Troubleshooting

### Common Issues

**pg_dump not found:**
- Install PostgreSQL client tools
- Ensure `pg_dump` is in system PATH

**Permission denied:**
- Check database user permissions
- Verify file system write permissions

**Backup file empty:**
- Check database connection
- Verify table names with prefix
- Review error logs

**Access denied:**
- Ensure admin login
- Check session validity
- Verify route permissions

## API Reference

### System Backup
```
GET /admin/backup
Authorization: Admin session required
Response: application/zip
```

### Monthly Guest Backup
```
GET /api/backup/guests?year=YYYY&month=MM[&format=json]
Authorization: Admin session required
Response: text/csv or application/json
```

### Error Responses
```json
{
  "error": "Missing year or month parameter"
}
```

## Support

For issues with backup functionality:
1. Check application logs
2. Verify database connectivity
3. Test with provided test scripts
4. Review configuration settings 