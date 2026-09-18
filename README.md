# SoulCraft — Django storefront

A small e-commerce demo implementing four requirements: a polished custom
front-end, a secure Django login system, "Continue with Google" via
django-allauth, and product management through a customized Django Admin.

## Quick start

```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows Git Bash (.venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
## SoulCraft

SoulCraft is a Django e-commerce storefront for browsing handcrafted products,
managing a session-based cart, placing demo orders, and managing the catalog
through a customized Django Admin interface.

The project includes a responsive custom frontend, email-first authentication,
Google OAuth through django-allauth, product image management, customer
support tickets, and a small rule-based support chatbot.

## Features

- Product catalog with search, category filtering, product details, pricing,
  stock information, and image galleries.
- Session-based shopping cart and demo checkout flow that records orders but
  does not process real payments.
- Custom email-based signup, login, logout, profile, and password validation.
- Optional "Continue with Google" login using Google OAuth 2.0.
- Staff-only Django Admin for categories, products, orders, users, and multiple
  product images.
- Support center with ticket submission and a CSRF-protected chatbot endpoint.
- Responsive styling for desktop and mobile screens.
- Security defaults including CSRF protection, hashed passwords, generic login
  errors, secure production cookies, and environment-based secrets.

## Technology

- Python
- Django
- django-allauth
- Pillow
- SQLite for local development
- HTML templates, CSS, and vanilla JavaScript

## Project Structure

```text
accounts/     Custom user model, authentication, forms, and OAuth adapters
config/       Django settings, URLs, ASGI, and WSGI configuration
store/        Catalog, cart, checkout, orders, and storefront views
support/      Support tickets and chatbot logic
templates/    Shared, account, store, support, and admin templates
static/       CSS and JavaScript assets
media/        Local uploaded product images; ignored by Git
```

## Requirements

- Python 3.10 or newer
- Git
- A Google Cloud project only if Google login is required

## Local Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies and create the local database:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser. The admin area is available at
`http://127.0.0.1:8000/admin/`.

## Environment Variables

Copy `.env.example` to `.env` and replace the placeholder values:

```powershell
Copy-Item .env.example .env
```

The `.env` file is ignored by Git and must never be committed.

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Secret used by Django sessions and signing |
| `DJANGO_DEBUG` | Use `1` locally and `0` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated production hostnames |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret |

For a production deployment, use a long random `DJANGO_SECRET_KEY`, set
`DJANGO_DEBUG=0`, and configure `DJANGO_ALLOWED_HOSTS` for the real domain.

## Google OAuth Setup

Google login is optional. To enable it:

1. Create an OAuth client in Google Cloud Console.
2. Add the local origins `http://127.0.0.1:8000` and
   `http://localhost:8000`.
3. Add these redirect URIs:
   - `http://127.0.0.1:8000/accounts/google/login/callback/`
   - `http://localhost:8000/accounts/google/login/callback/`
4. Put the client ID and secret in `.env`.
5. Restart the Django server.

This project registers the Google credentials from environment variables. Do
not also create a Google SocialApp record in Django Admin, because registering
the provider in two places can cause an allauth `MultipleObjectsReturned`
error.

## Demo Accounts

`python manage.py seed_data` creates demo users and catalog content for local
development. Change these passwords before using the project anywhere outside
local development.

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@soulcraft.test` | `AdminPass!2345` |
| Customer | `demo@soulcraft.test` | `DemoPass!2345` |

## Testing

Run the complete test suite:

```bash
python manage.py test
```

Run tests for an individual application:

```bash
python manage.py test accounts
python manage.py test store
python manage.py test support
```

Run Django's configuration checks:

```bash
python manage.py check
```

## Git and Secrets

The repository intentionally excludes `.env`, `.venv`, `*.sqlite3`, uploaded
media, generated static files, and local screenshots. The committed
`.env.example` file contains placeholders only.

Before the first push, check the staged file list:

```bash
git add .
git status
```

Make sure `.env` and any real credential files are not listed. If a real OAuth
secret has ever been committed, revoke it in Google Cloud Console and create a
new one before continuing.

## Current Limitations

- Checkout records an order but does not charge a payment method.
- Email verification is disabled for local development.
- Uploaded media is local-only and is not included in Git.
- Google OAuth requires a configured client ID and secret.

## License

No license has been selected for this repository yet. Add a license before
redistributing the project publicly.
  turn on once SMTP credentials exist.
- **Google OAuth**: code-complete; needs client ID/secret (see above).
