# E-Voting System - Implementation Guide

## Overview
This document provides a complete guide to the 15 new features implemented in the e-voting system.

---

## ✅ Feature 1: Strong Authentication (Email/Password + OTP or 2FA)

### Implementation Details
- **OTP System**: Time-based One-Time Password (TOTP) using PyOTP
- **Email OTP**: 6-digit codes sent to user email (5 min expiry)
- **2FA Setup**: Users can enable TOTP via authenticator apps

### Models
- `CustomUser`: Enhanced with `two_fa_enabled`, `otp_secret`, `email_verified`
- `OTPVerification`: Stores OTP records with expiry tracking

### Views
- `register_view`: Registration with CAPTCHA
- `verify_email`: OTP verification
- `setup_2fa`: 2FA setup wizard
- `confirm_2fa`: TOTP confirmation
- `login_view`: Login with 2FA support
- `verify_2fa`: 2FA verification during login

### API Endpoints
- `POST /api/token/` - Get JWT token (email/username + password)
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/otp/` - Request OTP
- `POST /api/otp/verify/` - Verify OTP

---

## ✅ Feature 2: Voter Verification (Unique ID/Citizenship-based)

### Implementation Details
- Store unique voter ID (citizenship number, passport, etc.)
- Verification status tracking (pending, verified, rejected, suspended)
- Admin verification workflow

### Models
- `VoterProfile`: Stores voter verification info
  - `unique_voter_id`: Citizenship/Voter ID number
  - `verification_status`: Current status
  - `verified_by`: Admin who verified
  - `verified_at`: Verification timestamp

### Views
- `complete_voter_profile`: User completes profile
- `verify_voters`: Admin verification interface

### Admin Features
- View pending verifications
- Approve/reject profiles with notes
- Track verification history

---

## ✅ Feature 3: Prevent Multiple Voting (One user = One vote)

### Implementation Details
- Database-level constraint: `UniqueConstraint(fields=['election', 'user'])`
- Backend checks in voting logic
- Vote deduplication in UI

### Model
- `Vote`: Has unique constraint preventing duplicate votes per election

### Protection Mechanisms
1. Database-level constraint
2. View-level checks before vote submission
3. Transaction-based atomic operations
4. Suspicious activity detection

---

## ✅ Feature 4: Live Results Dashboard (Real-time Charts/Graphs)

### Implementation Details
- Results with real-time data
- Chart.js integration for visualizations
- JSON API for live updates
- Admin control over result publication

### Views
- `results`: Main results view with charts
- `get_election_stats_json`: JSON API for live data

### Features
- Pie/bar charts showing vote distribution
- Live vote counts
- Percentage calculations
- Admin-only results until published

### API Endpoints
- `GET /api/elections/{id}/results/` - Get results
- `GET /api/elections/{id}/status/` - Get election status

---

## ✅ Feature 5: Admin Panel (Manage Elections & Candidates)

### Implementation Details
- Dedicated admin dashboard
- Election management interface
- Candidate management
- Vote verification workflow

### Views
- `admin_dashboard`: Overview with statistics
- `manage_elections`: List all elections
- `create_election`: Create new election
- `manage_candidates`: Manage candidates for election
- `add_candidate`: Add new candidate
- `verify_voters`: Voter profile verification

### Admin Features
- Real-time statistics
- Activity logs
- Recent votes tracking
- Quick action buttons

---

## ✅ Feature 6: Enhanced Candidate Profiles

### Implementation Details
- Comprehensive candidate information
- Photo/image support
- Political party information
- Biography and manifesto

### Model Updates - `Candidate`
- `photo`: Image upload support
- `party`: Political party name
- `symbol`: Party symbol
- `biography`: Detailed biography
- `position`: Display order
- `is_independent`: Independent candidate flag
- `email`, `phone`: Contact information

### Display Features
- Photo galleries
- Party symbol display
- Full biography on profile
- Enhanced voting form with candidate info

---

## ✅ Feature 7: Mobile Responsive Design

### Implementation Details
- Bootstrap 5 framework
- Mobile-first approach
- Responsive templates
- Touch-friendly interfaces

### Features
- Mobile-optimized layouts
- Responsive forms
- Mobile-safe voting interface
- Responsive data tables
- Mobile-friendly admin panel

### Breakpoints
- sm: 576px
- md: 768px
- lg: 992px
- xl: 1200px

---

## ✅ Feature 8: Enhanced UI/UX Design

### Implementation Details
- Clean, modern interface
- Intuitive voting flow
- Color-coded status indicators
- Clear visual hierarchy

### Components
- Card-based layouts
- Bootstrap components
- Consistent color scheme
- Status badges
- Progress indicators

### User Experience
1. Clear navigation
2. Minimal steps to vote
3. Confirmation messages
4. Error handling
5. Accessibility support

---

## ✅ Feature 9: Voting Time Control

### Implementation Details
- Start and end time settings per election
- Automatic voting window enforcement
- Admin control over voting period

### Model - `Election`
- `start_time`: Election start
- `end_time`: Election end
- `allow_voting`: Toggle voting (can disable while keeping results)

### Features
- Time-based voting restrictions
- Admin can enable/disable voting
- Automatic window checks
- Scheduled election support

### Helper Methods
- `is_voting_open()`: Check if voting is currently allowed
- `is_voting_closed()`: Check if voting period ended

---

## ✅ Feature 10: Secure Backend System (JWT + API Protection)

### Implementation Details
- JWT token-based authentication
- Role-based access control
- API rate limiting
- CORS configuration

### JWT Configuration
- 15-minute access token lifetime
- 7-day refresh token lifetime
- Token refresh rotation enabled

### Protection Features
- HTTPS required in production
- CSRF token protection
- Session security settings
- Secure cookie configuration
- API throttling (100/hour for anon, 1000/hour for users)

### API Endpoints
- All API endpoints require authentication
- Permission classes enforce security
- Token-based access

---

## ✅ Feature 11: Email Notifications

### Implementation Details
- Vote confirmation emails
- Admin notifications
- OTP emails
- Notification logging

### Email Types
1. **OTP Email**: 6-digit code for verification
2. **Vote Confirmation**: Sent after vote submission
3. **Admin Alerts**: Notifications for important events
4. **Verification Updates**: Profile verification status

### Configuration
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Model - `NotificationLog`
- Track all sent notifications
- Delivery status
- Error logging

---

## ✅ Feature 12: Vote Logs/History (Activity Tracking)

### Implementation Details
- Track all voting-related activities
- Transparent audit trail
- User activity history
- Admin activity logging

### Models
- `VoteLog`: User voting activities
- `AuditLog`: Admin/system actions

### Activity Types Tracked
- User login
- Vote attempts
- Vote submissions
- Verification events
- Admin actions

### Features
- User can view own history
- Admins can view all logs
- IP address tracking
- Timestamp recording
- Activity descriptions

---

## ✅ Feature 13: Anti-Bot Protection (CAPTCHA)

### Implementation Details
- Google reCAPTCHA v2 integration
- Bot activity detection
- Failed attempt tracking

### Configuration
```python
RECAPTCHA_PUBLIC_KEY = 'your-public-key'
RECAPTCHA_PRIVATE_KEY = 'your-private-key'
```

### Protection Mechanisms
1. CAPTCHA on registration
2. Failed login attempt tracking
3. IP-based bot detection
4. Rate limiting

### Model - `CaptchaLog`
- Track CAPTCHA attempts
- Pass/fail recording
- IP address logging

---

## ✅ Feature 14: Multi-language Support (English + Nepali)

### Implementation Details
- Django i18n framework
- Language preference storage
- Message translations

### Configuration
```python
LANGUAGES = [
    ('en', 'English'),
    ('ne', 'Nepali'),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
```

### Model Updates - `CustomUser`
- `language` field for preference storage

### View - `settings_view`
- Users can set language preference

### Features
- User language preference
- UI language switching
- Database-stored preferences

---

## ✅ Feature 15: Export Results Feature (PDF/Excel)

### Implementation Details
- PDF generation using ReportLab
- Excel export using openpyxl
- Admin-only functionality
- Formatted output

### Views
- `export_results_pdf`: Generate PDF report
- `export_results_excel`: Generate Excel file

### PDF Features
- Professional formatting
- Vote statistics table
- Election details header
- Timestamp

### Excel Features
- Multi-column layout
- Formatted cells
- Summary section
- Color-coded headers

### Data Included
- Election title
- All candidates
- Vote counts
- Percentages
- Total votes
- Export date/time

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
```env
# Email Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY=your-public-key
RECAPTCHA_PRIVATE_KEY=your-private-key

# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False  # In production
```

### 3. Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Server
```bash
python manage.py runserver
```

---

## URL Routes

### Public Routes
- `/` - Home page
- `/register/` - User registration
- `/login/` - User login
- `/verify-email/{user_id}/` - Email verification
- `/complete-voter-profile/` - Voter profile completion
- `/setup-2fa/` - 2FA setup
- `/confirm-2fa/` - 2FA confirmation
- `/verify-2fa/` - 2FA verification during login

### Authenticated Routes
- `/dashboard/` - User dashboard
- `/vote/{election_id}/` - Vote in election
- `/results/{election_id}/` - View election results
- `/vote-history/` - User activity log
- `/settings/` - Account settings
- `/export/results/{election_id}/pdf/` - Export PDF
- `/export/results/{election_id}/excel/` - Export Excel

### Admin Routes
- `/admin-dashboard/` - Admin overview
- `/manage-elections/` - Election management
- `/create-election/` - Create election
- `/manage-candidates/{election_id}/` - Candidate management
- `/add-candidate/{election_id}/` - Add candidate
- `/verify-voters/` - Voter verification
- `/admin/` - Django admin panel

### API Routes
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh token
- `GET/POST /api/elections/` - Elections CRUD
- `GET /api/elections/{id}/results/` - Election results
- `GET /api/elections/{id}/status/` - Election status
- `GET /api/candidates/` - List candidates
- `POST /api/votes/` - Submit vote
- `GET /api/votes/` - User votes
- `POST /api/voter-profiles/` - Voter profile
- `POST/GET /api/otp/` - OTP operations
- `GET /api/vote-logs/` - Activity logs
- `GET /api/notifications/` - User notifications

---

## Database Models Summary

### Core Models
1. **CustomUser** - Enhanced user with 2FA, OTP, language
2. **VoterProfile** - Voter verification info
3. **Election** - Election with time control
4. **Candidate** - Enhanced with profiles
5. **Vote** - Vote recording with IP tracking

### Audit/Logging Models
6. **VoteLog** - Activity tracking
7. **OTPVerification** - OTP records
8. **CaptchaLog** - CAPTCHA attempts
9. **NotificationLog** - Email/notification tracking
10. **AuditLog** - Admin action logging

---

## Security Features

### Authentication
- Password hashing (Django default)
- 2FA/TOTP support
- Email verification
- JWT tokens with expiry

### Voting Security
- One vote per user constraint
- Double-voting prevention
- IP address tracking
- Activity logging

### API Security
- JWT authentication
- CORS restriction
- Rate limiting
- Throttling

### Bot Protection
- CAPTCHA on registration
- Failed login tracking
- IP-based detection
- Request throttling

### Data Security
- HTTPS in production
- Secure cookies
- CSRF protection
- SQL injection prevention (ORM)

---

## Testing Checklist

- [ ] User registration with CAPTCHA
- [ ] Email OTP verification
- [ ] 2FA setup and verification
- [ ] Login with 2FA
- [ ] Voter profile completion
- [ ] Voter verification workflow
- [ ] Vote submission
- [ ] Vote prevention (duplicate)
- [ ] Results display
- [ ] PDF export
- [ ] Excel export
- [ ] Activity logs
- [ ] Email notifications
- [ ] Language preference
- [ ] Admin dashboard
- [ ] Candidate management
- [ ] Election management

---

## Troubleshooting

### Email Issues
- Check EMAIL settings in settings.py
- Verify SMTP credentials
- Use Gmail app passwords (not account password)
- Check firewall for port 587

### CAPTCHA Issues
- Verify public/private keys
- Check domain in reCAPTCHA settings
- Ensure JavaScript is enabled

### 2FA Issues
- Use compatible authenticator app (Google, Authy, etc.)
- Check server time sync
- Verify OTP secret storage

### API Issues
- Check JWT token expiry
- Verify CORS settings
- Check authentication headers
- Review rate limiting

---

## Future Enhancements

- Real-time WebSocket updates for results
- SMS-based OTP
- Biometric authentication
- Advanced analytics dashboard
- Mobile app
- Blockchain integration for transparency
- Distributed voting system
- Voter demographics tracking

---

## Support

For issues or questions:
1. Check Django logs
2. Review admin panel for activity
3. Check database integrity
4. Verify email configuration
5. Review security logs

---

## License

This project is part of the E-Voting System. All rights reserved.
