# E-Voting System - Setup & Migration Guide

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Key Packages Added
- **djangorestframework** - REST API framework
- **djangorestframework-simplejwt** - JWT authentication
- **pyotp** - Time-based OTP (TOTP)
- **qrcode** - QR code generation for 2FA
- **pillow** - Image handling
- **django-recaptcha** - CAPTCHA integration
- **openpyxl** - Excel file generation
- **reportlab** - PDF generation
- **django-cors-headers** - CORS support
- **crispy-forms** - Form rendering
- **django-filter** - Filtering for API
- **django-rosetta** - Translation management
- **channels** - WebSocket support
- **redis** - Caching/sessions

---

## Step 2: Environment Configuration

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Email Configuration (Gmail Example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# reCAPTCHA Configuration
RECAPTCHA_PUBLIC_KEY=your-recaptcha-public-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-private-key

# Database (optional, for PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/evoting

# Redis (optional, for caching)
REDIS_URL=redis://localhost:6379/0
```

### Getting Email Credentials (Gmail)

1. Enable 2-Factor Authentication on your Google Account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate an app password for "Mail" on "Windows PC"
4. Use this password (not your Google password) in EMAIL_HOST_PASSWORD

### Getting reCAPTCHA Keys

1. Go to: https://www.google.com/recaptcha/admin
2. Click "Create" or "+" button
3. Fill in the form:
   - Label: "E-Voting System"
   - reCAPTCHA type: "reCAPTCHA v2" → "I'm not a robot" Checkbox
   - Domains: localhost, yourdomain.com
4. Accept and submit
5. Copy Site Key (public) and Secret Key (private)

---

## Step 3: Database Migration

### Create Migration Files

```bash
python manage.py makemigrations voting
```

This will create migration files for all the new models:
- CustomUser enhancements
- VoterProfile
- Vote tracking
- VoteLog
- OTPVerification
- CaptchaLog
- NotificationLog
- AuditLog

### Apply Migrations

```bash
python manage.py migrate
```

This applies all migrations to your database.

### Migration Output (Expected)

```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, voting
Running migrations:
  Applying voting.0003_votingmodels...OK
  Applying voting.0004_otp_and_logging...OK
  Applying voting.0005_enhanced_security...OK
```

---

## Step 4: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
```
Username: admin
Email: admin@evoting.com
Password: ••••••••••
```

---

## Step 5: Create Necessary Directories

```bash
mkdir -p media/candidates
mkdir -p logs
mkdir -p locale
```

---

## Step 6: Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

---

## Step 7: Run Development Server

```bash
python manage.py runserver
```

Server will be available at: http://localhost:8000

---

## Verification Steps

### 1. Test Home Page
- Navigate to http://localhost:8000
- Should see home page with available elections

### 2. Test Registration
- Click "Register"
- Create account with email
- Check console/email for OTP

### 3. Test Admin Panel
- Navigate to http://localhost:8000/admin
- Login with superuser credentials
- Verify all models are listed

### 4. Test API
- Navigate to http://localhost:8000/api/
- Should see DRF browsable API interface
- Try to authenticate with token endpoint

---

## Docker Setup (Optional)

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "evoting.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: evoting
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    ports:
      - "8000:8000"
    environment:
      DEBUG: "True"
      DATABASE_URL: postgresql://postgres:password@db:5432/evoting
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - .:/app

volumes:
  postgres_data:
```

### Run with Docker

```bash
docker-compose up -d
```

---

## Production Deployment

### 1. Update settings.py

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
CSRF_TRUSTED_ORIGINS = ['https://yourdomain.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
```

### 2. Use Environment Variables

```bash
export SECRET_KEY="your-secret-key"
export DEBUG="False"
export ALLOWED_HOSTS="yourdomain.com"
```

### 3. Use PostgreSQL (Recommended)

Instead of SQLite in production.

### 4. Use Gunicorn

```bash
gunicorn evoting.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 5. Use Nginx Reverse Proxy

Configure Nginx to proxy requests to Gunicorn.

### 6. Use SSL Certificate

Get free SSL from Let's Encrypt:
```bash
certbot certonly --standalone -d yourdomain.com
```

---

## Troubleshooting

### Migration Conflicts

If migrations conflict with existing data:

```bash
python manage.py migrate --fake-initial
```

### Database Lock (SQLite)

Delete and recreate database:
```bash
rm db.sqlite3
python manage.py migrate
```

### Import Errors

Ensure all packages are installed:
```bash
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

Use a different port:
```bash
python manage.py runserver 8001
```

---

## Testing

### Run Tests

```bash
python manage.py test
```

### Create Test Data

```bash
python manage.py shell

from voting.models import CustomUser, Election
from django.utils import timezone
from datetime import timedelta

# Create test user
user = CustomUser.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)

# Create test election
election = Election.objects.create(
    title='Test Election',
    start_time=timezone.now(),
    end_time=timezone.now() + timedelta(days=1),
    created_by=user
)

print(f"Created user: {user}")
print(f"Created election: {election}")
```

---

## Next Steps

1. **Customize Templates**: Update templates in `templates/voting/`
2. **Configure Email**: Set up your email backend
3. **Add Candidates**: Use admin panel to add candidates
4. **Create Elections**: Create elections for testing
5. **Test Workflows**: Test registration, voting, results
6. **Deploy**: Deploy to production server

---

## Support Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## Quick Reference

### Useful Management Commands

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Interactive shell
python manage.py shell

# Export data
python manage.py dumpdata > backup.json

# Import data
python manage.py loaddata backup.json

# Collect static files
python manage.py collectstatic

# Clear cache
python manage.py clear_cache
```

### File Structure

```
Election/
├── evoting/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── voting/            # Main app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── utils.py
│   ├── api_views.py
│   ├── serializers.py
│   ├── admin.py
│   └── migrations/
├── templates/         # HTML templates
├── static/            # Static files
├── media/             # User uploads
├── logs/              # Log files
├── manage.py
└── requirements.txt
```

---

## Checklist

- [ ] Install dependencies
- [ ] Set environment variables
- [ ] Run migrations
- [ ] Create superuser
- [ ] Create directories
- [ ] Run development server
- [ ] Test registration
- [ ] Test login
- [ ] Test voting
- [ ] Test admin panel
- [ ] Test API
- [ ] Configure email
- [ ] Configure CAPTCHA
- [ ] Ready for deployment
