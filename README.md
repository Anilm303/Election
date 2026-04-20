# Electronic Voting System (Django + Vercel Serverless)

Minimal full-stack voting system using Django templates and serverless deployment on Vercel.

## 1) Project Structure

```text
Election/
├── api/
│   └── index.py
├── evoting/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── voting/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/
│   ├── base.html
│   └── voting/
│       ├── dashboard.html
│       ├── home.html
│       ├── login.html
│       ├── register.html
│       ├── results.html
│       └── vote.html
├── manage.py
├── requirements.txt
├── vercel.json
└── .gitignore
```

## 2) Features

- Custom User model
- Election, Candidate, Vote models
- Duplicate vote prevention by database constraint and view validation
- Login/register/dashboard/vote/results pages
- CSRF-protected forms
- Bootstrap UI via CDN
- Whitenoise static files support

## 3) Local Run (Optional)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open: http://127.0.0.1:8000

## 4) Environment Variables

Set these in Vercel Project Settings -> Environment Variables:

- `SECRET_KEY` = long random secret
- `DEBUG` = `False`
- `ALLOWED_HOSTS` = `.vercel.app,your-domain.com`
- `CSRF_TRUSTED_ORIGINS` = `https://*.vercel.app,https://your-domain.com`
- `DATABASE_URL` = PostgreSQL URL (Neon/Supabase recommended)

Notes:
- If `DATABASE_URL` is missing, app uses SQLite (good for demo/local).
- In production serverless, use PostgreSQL.

## 5) Deploy to GitHub + Vercel

### Push to GitHub

```bash
git init
git add .
git commit -m "Initial Django voting system for Vercel"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Import in Vercel

1. Open Vercel dashboard.
2. Click "Add New" -> "Project".
3. Import the GitHub repo.
4. Add the environment variables listed above.
5. Deploy.

## 6) Common Errors and Fixes

### "Application not found"

Checklist:
- `vercel.json` exists at root.
- `api/index.py` exists and exports `app`.
- `DJANGO_SETTINGS_MODULE` is set in `api/index.py`.

### Static files not loading

Checklist:
- `whitenoise.middleware.WhiteNoiseMiddleware` is in middleware.
- `STATIC_ROOT = BASE_DIR / "staticfiles"` is configured.
- `STATICFILES_STORAGE` is set to Whitenoise compressed storage.
- Templates use `{% load static %}` and static tag correctly.

### Database issues in production

Checklist:
- Set valid `DATABASE_URL` to PostgreSQL.
- Ensure PostgreSQL allows connections from Vercel.
- Run migrations using local machine against production DB URL:

```bash
set DATABASE_URL=postgresql://...
python manage.py migrate
```

## 7) Security Notes

- Voting is login-protected.
- One vote per user per election is enforced in DB and code.
- CSRF protection is enabled by default.
- Forms are validated server-side.
