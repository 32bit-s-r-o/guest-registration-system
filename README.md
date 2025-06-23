# Guest Registration System

A secure, GDPR-compliant guest registration system built with Flask and PostgreSQL. This application allows trip organizers to create registration forms for their trips and collect guest information including identification documents.

## Features

### For Trip Organizers (Admins)
- Create and manage trips with custom dates and guest limits
- Review and approve/reject guest registrations
- Automatic email notifications for approval/rejection
- GDPR-compliant document handling (automatic deletion after approval)
- Admin dashboard with statistics and management tools
- **Data management tools for reset and seeding**
- **Contact information management for guest communications**
- **Multi-language Support**: English and Czech translations with language picker
- **Language Picker Control**: Option to disable language picker and force English

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

# Table Prefix Configuration
# This prefix will be added to all database table names
# Default: guest_reg_ (creates tables like guest_reg_admin, guest_reg_trip, etc.)
# You can change this to avoid conflicts with existing tables
TABLE_PREFIX=guest_reg_

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Language Picker Configuration
LANGUAGE_PICKER_ENABLED=true
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

## Data Management

The application includes comprehensive data management tools for development, testing, and demonstration purposes.

### Command Line Tools

Use the `reset_data.py` script for data management operations:

```bash
# Reset all data (drop and recreate tables)
python reset_data.py reset

# Seed with sample data (admin, trips, registrations)
python reset_data.py seed

# Reset and seed in one command
python reset_data.py reset-seed

# Show database statistics
python reset_data.py stats
```

### Web Interface

Access data management through the admin panel:

1. **Login to Admin Panel**: `http://localhost:5000/admin/login`
2. **Navigate to Data Management**: Click "Data Management" in the Quick Actions
3. **View Statistics**: See current database counts and registration status
4. **Reset Data**: Permanently delete all data (with confirmation)
5. **Seed Data**: Add sample data for testing

### Sample Data Created

When seeding data, the system creates:

- **Sample Admin**: username: `admin`, password: `admin123`
- **Sample Trips**: 3 trips with different dates and guest limits
- **Sample Registrations**: Various registrations in pending, approved, and rejected states
- **Sample Guests**: Multiple guests with different document types

## Airbnb Calendar Integration

The application includes powerful Airbnb calendar integration that automatically syncs reservations and creates registration forms.

### Features

- **Automatic Sync**: Import reservations directly from your Airbnb calendar
- **Real-time Updates**: Changes to reservations are automatically reflected
- **Guest Information**: Extract guest names and counts from calendar events
- **Manual Sync**: Trigger sync manually from the trips page
- **Secure**: Calendar URLs are stored securely and not shared

### Setup Instructions

1. **Get Your Airbnb Calendar URL**:
   - Go to your Airbnb listing
   - Click the "Calendar" tab
   - Click "Export Calendar"
   - Copy the iCal URL (format: `https://www.airbnb.com/calendar/ical/YOUR_LISTING_ID.ics?s=YOUR_SECRET_KEY`)

2. **Configure in Admin Settings**:
   - Login to admin panel
   - Go to Settings page
   - Enter your Airbnb Listing ID
   - Paste your calendar URL
   - Enable sync

3. **Sync Reservations**:
   - Use the "Sync Airbnb" button on the trips page
   - Or enable automatic sync in settings

### How It Works

1. **Calendar Fetching**: System fetches your Airbnb calendar using the iCal URL
2. **Reservation Parsing**: Extracts reservation details (dates, guest info, etc.)
3. **Trip Creation**: Automatically creates registration forms for each reservation
4. **Guest Information**: Populates trip details with guest names and counts
5. **Confirmation Codes**: Extracts and stores Airbnb confirmation codes for easy access

## Contact Information Management

The admin settings include comprehensive contact information management for guest communications and contact pages.

### Contact Information Fields

Admins can configure the following contact details in the Settings page:

- **Contact Name**: The name to display for contact purposes
- **Phone Number**: Contact phone number for guests
- **Address**: Business or property address
- **Website**: Your website URL (optional)
- **Description**: Brief description about your property or business

### Usage

The contact information is used in:

1. **Contact Page**: Public contact page at `/contact` displaying all contact details
2. **Guest Communications**: Can be included in email notifications
3. **Admin Settings**: Centralized management of all contact information
4. **Future Integration**: Ready for integration with other parts of your website

### Setting Up Contact Information

1. **Login to Admin Panel**: `http://localhost:5000/admin/login`
2. **Go to Settings**: Click "Settings" in the admin dashboard
3. **Fill Contact Information**: Enter your contact details in the "Contact Information" section
4. **Save Settings**: Click "Save Settings" to update

### Contact Page

The public contact page (`/contact`) automatically displays:
- Contact person name and phone number
- Email address and website links
- Full address with proper formatting
- Contact form for guest inquiries
- About section with your description

## Confirmation Code Registration

The system supports Airbnb confirmation codes for streamlined guest registration.

### Registration Flow

Guests can register using two methods:

1. **Confirmation Code Entry** (`/register`):
   - Landing page with confirmation code form
   - Guests enter their Airbnb confirmation code
   - System validates and redirects to registration form

2. **Direct Confirmation Code Link** (`/register/<code>`):
   - Direct access using confirmation code in URL
   - No need to enter code manually
   - Perfect for sharing in emails or messages

3. **Traditional Trip ID Link** (`/register/id/<trip_id>`):
   - Direct access using trip ID
   - Works for both Airbnb and manual trips

### Confirmation Code Extraction

The system automatically extracts confirmation codes from Airbnb calendar events using pattern matching:

- **Patterns Supported**:
  - "Confirmation code: ABC123"
  - "Code: ABC123" 
  - "ABC123" (standalone codes)
- **Format**: 6+ character alphanumeric codes
- **Case**: Automatically converted to uppercase

### Admin Features

- **View Confirmation Codes**: See codes in trip details
- **Copy Links**: Easy copy buttons for both registration methods
- **Direct Access**: Use confirmation codes to quickly access registrations
- **Validation**: System validates codes before allowing registration

### Benefits

- **User-Friendly**: Guests don't need to remember trip IDs
- **Professional**: Clean URLs with confirmation codes
- **Flexible**: Multiple registration methods supported
- **Secure**: Codes are validated against existing trips
- **Convenient**: Easy sharing via email or messaging apps

### What Gets Synced

- ✅ Reservation dates (check-in/check-out)
- ✅ Guest names (when available)
- ✅ Number of guests
- ✅ Reservation status
- ✅ Reservation updates

### What Doesn't Get Synced

- ❌ Guest contact information (for privacy)
- ❌ Payment information
- ❌ Messages and reviews
- ❌ House rules and policies

### Privacy & Security

- Calendar URLs are encrypted and stored securely
- Only reservation data is imported (no personal details)
- GDPR compliance maintained for all imported data
- No access to Airbnb account credentials

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
├── reset_data.py         # Data reset and seeding script
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
│       ├── settings.html
│       ├── new_trip.html
│       ├── trips.html
│       ├── registrations.html
│       ├── view_registration.html
│       └── data_management.html
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

### Table Prefix Configuration

The application uses a configurable table prefix to avoid conflicts with existing database tables. By default, all tables are created with the `guest_reg_` prefix:

- `guest_reg_admin` - Admin users
- `guest_reg_trip` - Trips
- `guest_reg_registration` - Registrations  
- `guest_reg_guest` - Guests

#### Customizing Table Prefix

You can change the table prefix by setting the `TABLE_PREFIX` environment variable:

```env
# Use a different prefix
TABLE_PREFIX=myapp_

# This will create tables like:
# myapp_admin, myapp_trip, myapp_registration, myapp_guest
```

#### Benefits of Table Prefixing

- **Avoid Conflicts**: Prevents naming conflicts with existing tables
- **Multi-Tenant**: Run multiple instances in the same database
- **Organization**: Clearly identify application tables
- **Migration Safety**: Easy to identify and manage application data

#### Viewing Table Structure

Use the reset script to view your current table structure:

```bash
python reset_data.py tables
```

This will show:
- Current table prefix
- All table names
- Foreign key relationships

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
| `TABLE_PREFIX` | Database table prefix | No | guest_reg_ |
| `MAIL_SERVER` | SMTP server for emails | No | smtp.gmail.com |
| `MAIL_PORT` | SMTP port | No | 587 |
| `MAIL_USERNAME` | Email username | Yes | - |
| `MAIL_PASSWORD` | Email password/app password | Yes | - |
| `LANGUAGE_PICKER_ENABLED` | Enable language picker | No | true |

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
- `GET /admin/settings` - Admin settings page
- `POST /admin/settings` - Update admin settings
- `POST /admin/sync-airbnb` - Sync with Airbnb calendar
- `GET /admin/trips` - Manage trips
- `POST /admin/trips/new` - Create new trip
- `GET /admin/registrations` - Review registrations
- `GET /admin/registration/<id>` - View registration details
- `POST /admin/registration/<id>/approve` - Approve registration
- `POST /admin/registration/<id>/reject` - Reject registration
- `GET /admin/data-management` - Data management interface
- `POST /admin/reset-data` - Reset all data
- `POST /admin/seed-data` - Seed sample data
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
   - Run `  ` to create admin user
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

## Translation System

The app supports multiple languages using Flask-Babel:

- **English** (default)
- **Czech** (Čeština)

### Managing Translations

1. Extract translation strings: `python extract_translations.py`
2. Edit translation files in `translations/[lang]/LC_MESSAGES/messages.po`
3. Compile translations: `python extract_translations.py --compile`

### Language Picker

The language picker allows users to switch between available languages. When disabled, the app automatically uses English and hides the language selection interface. 