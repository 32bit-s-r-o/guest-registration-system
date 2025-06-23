# Housekeeping System Documentation

[← Back to Documentation Index](../docs/README.md)

## Overview

The Housekeeping System is a comprehensive task management solution for cleaning staff, featuring photo uploads, bulk operations, amenity assignments, and detailed task tracking. This system integrates with the accommodation management to automatically create housekeeping tasks.

## Quick Start

```bash
# Access housekeeper portal
http://localhost:5000/housekeeper/login

# View housekeeping tasks
http://localhost:5000/admin/housekeeping

# Manage amenities
http://localhost:5000/admin/amenities
```

## System Features

### ✅ Core Features
- **Task Management** - Create, update, and track housekeeping tasks
- **Photo Uploads** - Multiple photos per task with validation
- **Bulk Operations** - Update multiple tasks simultaneously
- **Amenity System** - Assign housekeepers to specific amenities
- **Status Tracking** - Complete workflow from pending to completed
- **Pay Calculation** - Automatic pay calculation based on completed tasks
- **Calendar Integration** - Tasks linked to accommodation dates

### ✅ User Roles
- **Admin** - Full housekeeping management and oversight
- **Housekeeper** - Task viewing, updates, and photo uploads

## Housekeeper Portal

### Login and Dashboard

Housekeepers can access their dedicated portal at `/housekeeper/login` with:
- Task overview and status
- Pay summary
- Calendar view
- Photo upload interface

### Task Management

Housekeepers can:
- View assigned tasks
- Update task status
- Add notes and comments
- Upload multiple photos
- Mark tasks as completed

### Photo Upload System

**Features:**
- Multiple photos per task
- Automatic file validation
- Secure storage
- Photo management interface

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)

**Size Limits:**
- Maximum file size: 16MB per photo
- Unlimited photos per task

## Admin Management

### Housekeeping Dashboard

Access via `/admin/housekeeping` with:
- Complete task overview
- Filtering by amenity and status
- Bulk update functionality
- Task detail views
- Photo management

### Task Creation

Tasks are automatically created when:
- New accommodations are added
- Calendar events are synced
- Manual task creation by admin

### Bulk Operations

**Available Actions:**
- Bulk status updates
- Bulk reassignment
- Bulk deletion
- Bulk photo management

**Usage:**
1. Select multiple tasks
2. Choose action from dropdown
3. Apply changes to all selected tasks

## Amenity System

### Amenity Management

**Features:**
- Create and manage property amenities
- Assign housekeepers to amenities
- Track amenity-specific tasks
- Filter tasks by amenity

**Amenity Types:**
- Cleaning services
- Maintenance tasks
- Specialized services
- Custom amenities

### Housekeeper Assignments

**Assignment Process:**
1. Create amenity in admin panel
2. Assign housekeeper to amenity
3. Tasks automatically assigned based on assignments
4. Housekeeper receives notifications

## Task Status Workflow

### Status Types

1. **Pending** - Task created, not yet started
2. **In Progress** - Task being worked on
3. **Completed** - Task finished successfully
4. **Cancelled** - Task cancelled or not needed

### Status Rules

**Housekeepers:**
- Can only mark tasks as completed on the task date
- Can update status to "In Progress"
- Can add notes and photos

**Admins:**
- Can change any task status at any time
- Can perform bulk status updates
- Can reassign tasks between housekeepers

## Pay System

### Pay Calculation

**Features:**
- Configurable default pay per task
- Automatic calculation for completed tasks
- Pay summary for housekeepers
- Admin oversight of payments

**Configuration:**
```bash
# Set default pay per task
DEFAULT_HOUSEKEEPER_PAY=25.00

# Currency for payments
HOUSEKEEPER_CURRENCY=EUR
```

### Pay Summary

Housekeepers can view:
- Total completed tasks
- Total earnings
- Task history
- Payment breakdown

## Photo Management

### Upload Interface

**Features:**
- Drag-and-drop upload
- Multiple file selection
- Progress indicators
- Preview functionality

### Storage and Security

**Storage:**
- Photos stored in `uploads/housekeeping/`
- Organized by task ID
- Automatic cleanup for deleted tasks

**Security:**
- File type validation
- Size limit enforcement
- Secure file handling
- Access control

## Calendar Integration

### Task Scheduling

**Automatic Creation:**
- Tasks created based on accommodation dates
- End date determines task date
- Automatic assignment to available housekeepers

### Calendar View

**Features:**
- Monthly calendar overview
- Task status indicators
- Date-based filtering
- Quick task access

## API Endpoints

### Housekeeper API

```bash
# Get housekeeper tasks
GET /api/housekeeper/tasks

# Update task status
POST /api/housekeeper/task/<id>/status

# Upload photos
POST /api/housekeeper/task/<id>/photos

# Get pay summary
GET /api/housekeeper/pay-summary
```

### Admin API

```bash
# Get all housekeeping tasks
GET /api/admin/housekeeping

# Bulk update tasks
POST /api/admin/housekeeping/bulk-update

# Manage amenities
GET /api/admin/amenities
POST /api/admin/amenities
```

## Configuration

### Environment Variables

```bash
# Housekeeping settings
DEFAULT_HOUSEKEEPER_PAY=25.00
HOUSEKEEPER_CURRENCY=EUR
ENABLE_HOUSEKEEPING_PHOTOS=true
MAX_HOUSEKEEPING_PHOTO_SIZE=16777216
ENABLE_BULK_HOUSEKEEPING_OPERATIONS=true
RESTRICT_TASK_COMPLETION_DATE=true

# Amenity system
ENABLE_AMENITY_SYSTEM=true
ENABLE_AMENITY_HOUSEKEEPER_ASSIGNMENTS=true
```

### Database Tables

**Core Tables:**
- `housekeeping_task` - Main task information
- `housekeeping_photo` - Task photos
- `amenity` - Property amenities
- `amenity_housekeeper` - Housekeeper assignments

## Testing

### Test Commands

```bash
# Test housekeeping system
python test_amenity_housekeeper_system.py

# Test photo uploads
python -c "from app import app; print('Photo system OK')"

# Test bulk operations
python manage.py test
```

### Test Coverage

**Covered Areas:**
- Task creation and management
- Photo upload functionality
- Bulk operations
- Amenity assignments
- Status updates
- Pay calculations

## Troubleshooting

### Common Issues

1. **Photo Upload Failures**
   - Check file size limits
   - Verify file format
   - Check upload directory permissions

2. **Task Assignment Issues**
   - Verify amenity-housekeeper assignments
   - Check task creation triggers
   - Review calendar integration

3. **Pay Calculation Errors**
   - Verify default pay settings
   - Check task completion status
   - Review pay calculation logic

### Debug Commands

```bash
# Check housekeeping status
python manage.py status

# Verify photo uploads
ls -la uploads/housekeeping/

# Test amenity assignments
python -c "from app import AmenityHousekeeper; print('Amenity system OK')"
```

## Best Practices

### Task Management

1. **Regular Updates**
   - Update task status promptly
   - Add detailed notes
   - Upload photos for completed tasks

2. **Photo Documentation**
   - Take clear, well-lit photos
   - Document before and after states
   - Include relevant details

3. **Communication**
   - Use notes for important information
   - Report issues immediately
   - Maintain clear task descriptions

### Admin Oversight

1. **Regular Monitoring**
   - Review task completion rates
   - Monitor photo uploads
   - Track housekeeper performance

2. **Quality Control**
   - Review uploaded photos
   - Verify task completion
   - Provide feedback to housekeepers

## Related Documentation

- [User Management](user-management.md) - Role-based access control
- [Accommodation Management](accommodation-management.md) - Task creation triggers
- [Calendar System](calendar-system.md) - Integration with scheduling
- [File Management](file-management.md) - Photo upload system

## Support

For housekeeping system issues:

1. Check task assignments and permissions
2. Verify photo upload configuration
3. Review amenity-housekeeper assignments
4. Test bulk operations functionality

---

**Last Updated**: January 2025  
**Version**: 1.8.0  
**Status**: Production Ready ✅

[← Back to Documentation Index](../docs/README.md) 