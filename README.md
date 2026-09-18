# SoulCraft

SoulCraft is a Django e-commerce storefront for browsing handcrafted products,
managing a session-based cart, placing demo orders, and managing a product
catalog through a customized Django Admin interface.

It was built as a full-stack internship project with four main goals:

1. Create a polished, responsive storefront.
2. Implement secure email-based authentication.
3. Add optional Google OAuth login.
4. Provide staff tools for managing products and orders.

## What Users Can Do

### Customers

- Browse the product catalog from the dashboard.
- Search products and filter them by category.
- Open a product detail page with stock, pricing, and image gallery data.
- Add items to a session-based cart and update quantities.
- Submit a demo checkout order.
- Create an account, sign in with email, or use Google OAuth.
- View a profile and submit support tickets.
- Ask common questions through the support chatbot.

### Staff

- Sign in through the Django Admin.
- Create and edit categories and products.
- Add multiple product images using the inline image editor.
- Review customer accounts, orders, and support tickets.
- Restrict catalog management to staff users.

## Main Routes

| Route | Purpose |
| --- | --- |
| `/` | Store dashboard and product catalog |
| `/product/<slug>/` | Product details and add-to-cart actions |
| `/cart/` | View and update the session cart |
| `/checkout/` | Submit a demo order |
| `/accounts/login/` | Email login and Google login button |
| `/accounts/signup/` | Create a customer account |
| `/accounts/profile/` | View the signed-in user's profile |
| `/support/` | Support tickets and chatbot |
| `/admin/` | Staff-only Django Admin |

## Features

- Product catalog with search, category filtering, stock information, pricing,
  and image galleries.
- Session-based cart that does not require an account before browsing.
- Demo checkout that records orders but does not process real payments.
- Custom email-first user model and authentication forms.
- Optional Google OAuth 2.0 through django-allauth.
- Staff-only administration with product image inlines.
- Support tickets and a small rule-based chatbot.
- Responsive custom CSS and vanilla JavaScript frontend.
- CSRF protection on state-changing requests.
- Password hashing through Django's password hashers.
- Production security settings activated when `DJANGO_DEBUG=0`.

## Technology

- Python 3.10 or newer
- Django 5.x
- django-allauth
- Pillow for product image handling
- python-dotenv for local environment files
- SQLite for local development
- Django templates, CSS, and vanilla JavaScript

## Architecture

```text
accounts/     Custom user model, authentication, forms, and OAuth adapters
config/       Settings, URL configuration, ASGI, and WSGI entry points
store/        Categories, products, images, cart, checkout, and orders
support/      Support tickets, forms, views, and chatbot rules
templates/    Shared, account, store, support, and admin templates
static/       Application CSS and JavaScript
media/        Local uploaded product images; excluded from Git
```

The main data flow is:

1. Staff create categories, products, stock values, and images in Admin.
2. Store views read the catalog and render product cards and detail pages.
3. Cart contents are stored in the user's Django session.
4. Checkout converts the cart into an order and order items.
5. Authentication uses the custom user model and Django sessions.

## Requirements

- Python 3.10 or newer
- Git
- A Google Cloud project only if Google login is needed

## Local Installation

Clone the repository:

```bash
git clone https://github.com/vivek061205/SoulCraft---Mini-HandCraft-Ecommerce-Store-.git
cd SoulCraft---Mini-HandCraft-Ecommerce-Store-
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies, initialize the database, and load demo content:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin area is at
`http://127.0.0.1:8000/admin/`.

## Environment Variables

Create a local environment file from the committed template:

```powershell
Copy-Item .env.example .env
```

Then replace the placeholder values in `.env`:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Secret used for Django signing and sessions |
| `DJANGO_DEBUG` | Use `1` locally and `0` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hostnames |
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth client secret |

`.env` is ignored by Git. Never commit it or paste its contents into an issue,
pull request, screenshot, or public chat.

## Google OAuth Setup

Google login is optional. In Google Cloud Console, create an OAuth web client
and configure the following local values:

**Authorized JavaScript origins**

```text
http://127.0.0.1:8000
http://localhost:8000
```

**Authorized redirect URIs**

```text
http://127.0.0.1:8000/accounts/google/login/callback/
http://localhost:8000/accounts/google/login/callback/
```

Put the client ID and secret in `.env`, then restart the server. The project
registers the provider from environment variables, so do not also create a
Google SocialApp record in Django Admin. Registering it in both places can
cause an allauth `MultipleObjectsReturned` error.

## Demo Data

The `seed_data` management command creates demo users, categories, products,
and local catalog images. Run it only for local development.

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin@soulcraft.test` | `AdminPass!2345` |
| Customer | `demo@soulcraft.test` | `DemoPass!2345` |

These are development credentials. Change them before deploying or sharing a
running instance.

Other useful commands:

```bash
python manage.py createsuperuser
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

## Testing and Checks

Run the complete test suite:

```bash
python manage.py test
```

Run tests for one application:

```bash
python manage.py test accounts
python manage.py test store
python manage.py test support
```

Run Django's configuration check:

```bash
python manage.py check
```

## Security Notes

- Passwords are hashed by Django and are never stored as plaintext.
- Login failures use a generic message rather than revealing which field was
  incorrect.
- CSRF middleware protects POST requests, including logout and checkout.
- Sessions use `HttpOnly` and `SameSite=Lax` cookie settings.
- When `DJANGO_DEBUG=0`, secure cookies, HTTPS redirect, HSTS, and related
  production protections are enabled.
- OAuth tokens are not stored at rest by the allauth configuration.
- Secrets are loaded from environment variables rather than source code.

## Deployment Checklist

Before deploying to a public host:

- Set a long random `DJANGO_SECRET_KEY` in the host's secret manager.
- Set `DJANGO_DEBUG=0`.
- Set `DJANGO_ALLOWED_HOSTS` to the real domain.
- Use a production database instead of local SQLite when appropriate.
- Configure HTTPS and update OAuth origins and redirect URIs.
- Configure persistent media storage for uploaded product images.
- Run migrations and `collectstatic` during deployment.
- Configure email verification and SMTP credentials if required.
- Replace all demo passwords and review staff accounts.
- Add payment processing only after configuring a real payment provider.

## Git and Secrets

The repository excludes `.env`, `.venv`, SQLite databases, uploaded media,
generated static files, and local screenshots. `.env.example` contains
placeholders only and is safe to publish.

Before committing changes, inspect the staged file list:

```bash
git add .
git status
```

If a real secret is ever committed, remove it from the repository history and
revoke or rotate it at the provider immediately. Deleting it in a later commit
does not make the old secret safe.

## Current Limitations

- Checkout records orders but does not charge a payment method.
- Email verification is disabled for local development.
- Uploaded media is local-only and is not included in Git.
- Google OAuth requires a configured client ID and secret.
- No license has been selected yet for redistribution.

## Contributing

1. Create a feature branch.
2. Keep secrets in `.env`, never in source files.
3. Add or update tests for behavior changes.
4. Run `python manage.py check` and `python manage.py test`.
5. Open a pull request describing the change and its verification steps.
