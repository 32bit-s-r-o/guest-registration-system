# Guest Registration System

A secure, GDPR-compliant guest registration system built with Flask and PostgreSQL. This application allows trip organizers to create registration forms for their trips and collect guest information including identification documents.

## Features

### For Trip Organizers (Admins)
- Create and manage trips with custom dates and guest limits
- Review and approve/reject guest registrations
- Automatic email notifications for approval/rejection
- GDPR-compliant document handling (automatic deletion after approval)
- Admin dashboard with statistics and management tools

### For Guests
- Simple registration form with document upload
- Support for multiple document types (passport, driving license, citizen ID)
- GDPR consent management
- Email notifications for registration status
- Mobile-responsive design

### Security & Compliance
- GDPR-compliant data handling
- Automatic document deletion after approval
- Secure file uploads with virus scanning
- Encrypted data storage
- Session management and authentication

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **Email**: Flask-Mail
- **File Handling**: Pillow, Werkzeug
- **Forms**: Flask-WTF, WTForms

## Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database (already configured)
- pip (Python package manager)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd airbnb

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Configuration

Your PostgreSQL database is already configured:
- **Host**: localhost
- **Port**: 5432
- **Database**: ekom21
- **User**: postgres
- **Password**: postgres

The application will automatically create the required tables in your existing database.

### 3. Environment Configuration

```bash
# Copy the example configuration
cp config.env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required .env configuration:**
```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production

# Database Configuration (already configured for your setup)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ekom21

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 4. Initialize the Application

```bash
# Run the setup script to create tables and admin user
python setup.py
```

The setup script will:
- Check your environment configuration
- Test database connectivity to your ekom21 database
- Create all database tables in your existing database
- Guide you through creating the first admin user

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage Guide

### Admin Workflow

1. **Access Admin Panel**
   - Navigate to `http://localhost:5000/admin/login`
   - Use the credentials you created during setup

2. **Create Your First Trip**
   - Click "Create New Trip" from the dashboard
   - Fill in trip details:
     - **Title**: Descriptive name (e.g., "Summer Beach Vacation 2024")
     - **Start Date**: Trip start date
     - **End Date**: Trip end date
     - **Max Guests**: Maximum number of guests allowed

3. **Share Registration Link**
   - After creating a trip, copy the registration link
   - Share this link with your guests via email, messaging, etc.

4. **Review Submissions**
   - Check the "Review Registrations" section for new submissions
   - Review guest information and uploaded documents
   - Approve or reject with comments

### Guest Workflow

1. **Access Registration**
   - Use the link provided by the trip organizer
   - Enter a contact email (one per group)

2. **Add Guest Information**
   - Fill in details for each guest:
     - First and last name
     - Document type (passport, driving license, or citizen ID)
     - Document number
     - Upload a clear photo of the document
     - Provide GDPR consent

3. **Review and Submit**
   - Review all entered information
   - Submit for admin approval

4. **Receive Notification**
   - Get email notification of approval/rejection
   - If rejected, follow the provided link to update information

## File Structure

```
airbnb/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── setup.py              # Initialization script
├── config.env.example    # Environment configuration template
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── register.html    # Registration form
│   ├── confirm.html     # Confirmation page
│   ├── success.html     # Success page
│   ├── about.html       # About page
│   ├── gdpr.html        # GDPR policy
│   └── admin/           # Admin templates
│       ├── login.html   # Admin login
│       ├── dashboard.html
│       ├── new_trip.html
│       ├── trips.html
│       ├── registrations.html
│       └── view_registration.html
├── static/              # Static files
│   └── uploads/         # Uploaded documents (auto-created)
└── uploads/             # Temporary file storage
```

## Database Schema

The application will create the following tables in your `ekom21` database:

### Tables

- **Admin**: Admin user accounts and authentication
- **Trip**: Trip information (title, dates, max guests, admin_id)
- **Registration**: Guest registration records (trip_id, email, status, admin_comment)
- **Guest**: Individual guest information (name, documents, GDPR consent)

### GDPR Compliance Features

- Document images automatically deleted after approval
- Personal data retention limited to 2 years
- Clear consent management for each guest
- Secure file handling and storage
- User rights information in GDPR policy

## Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | - |
| `DATABASE_URL` | PostgreSQL connection string | Yes | postgresql://postgres:postgres@localhost:5432/ekom21 |
| `MAIL_SERVER` | SMTP server for emails | No | smtp.gmail.com |
| `MAIL_PORT` | SMTP port | No | 587 |
| `MAIL_USERNAME` | Email username | Yes | - |
| `MAIL_PASSWORD` | Email password/app password | Yes | - |

### File Upload Settings

- **Maximum file size**: 16MB
- **Supported formats**: JPG, PNG
- **Storage location**: `uploads/` directory
- **Security**: Files renamed with UUID for security
- **Cleanup**: Automatic deletion after approval

## Security Features

- **Password Security**: Werkzeug password hashing
- **Session Management**: Flask-Login with secure sessions
- **CSRF Protection**: Flask-WTF CSRF tokens
- **File Upload Security**: Secure filename handling, size limits
- **Input Validation**: Comprehensive form validation
- **Access Control**: Admin-only routes protected
- **GDPR Compliance**: Automatic data cleanup

## API Endpoints

### Public Routes
- `GET /` - Home page
- `GET /about` - About page
- `GET /gdpr` - GDPR policy
- `GET /register/<trip_id>` - Registration form
- `POST /register/<trip_id>` - Submit registration
- `GET /confirm` - Confirmation page
- `POST /submit` - Final submission
- `GET /success` - Success page

### Admin Routes (Protected)
- `GET /admin/login` - Admin login page
- `POST /admin/login` - Admin authentication
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/trips` - Manage trips
- `POST /admin/trips/new` - Create new trip
- `GET /admin/registrations` - Review registrations
- `GET /admin/registration/<id>` - View registration details
- `POST /admin/registration/<id>/approve` - Approve registration
- `POST /admin/registration/<id>/reject` - Reject registration
- `GET /uploads/<filename>` - Serve uploaded files (admin only)

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running on localhost:5432
   - Check that the ekom21 database exists
   - Ensure postgres user has access to the database
   - Verify DATABASE_URL in .env file

2. **Email Not Sending**
   - Check MAIL_USERNAME and MAIL_PASSWORD
   - For Gmail, use App Password instead of regular password
   - Verify SMTP settings

3. **File Upload Issues**
   - Check uploads/ directory permissions
   - Verify file size is under 16MB
   - Ensure file format is JPG or PNG

4. **Admin Login Problems**
   - Run `python setup.py` to create admin user
   - Check username/password
   - Verify database tables exist

### Development Mode

For development, the app runs with debug mode enabled:
```bash
python app.py
```

For production, set `FLASK_ENV=production` and use a proper WSGI server like Gunicorn.

## Deployment

### Production Considerations

1. **Use a Production WSGI Server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Set Production Environment Variables**
   ```env
   FLASK_ENV=production
   SECRET_KEY=your-production-secret-key
   ```

3. **Configure Reverse Proxy** (Nginx/Apache)

4. **Set Up SSL Certificate**

5. **Configure Database Backups**

6. **Set Up Monitoring and Logging**

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- **Email**: support@guestregistration.com
- **Documentation**: [Link to documentation]
- **Issues**: Create an issue in the repository

## Changelog

### Version 1.0.0
- Initial release
- Complete registration workflow
- Admin panel with trip management
- GDPR compliance features
- Email notification system
- Secure file upload and handling
- Mobile-responsive design
- Comprehensive documentation 