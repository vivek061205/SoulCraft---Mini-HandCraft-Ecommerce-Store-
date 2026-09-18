# Session Notes — SoulCraft (read me first next session)

_Last worked on: Sep 16, 2026. Handoff notes for continuing development._

## What this project is

A Django e-commerce storefront ("SoulCraft") built **from scratch** in
`D:\Internship project` against a 4-part requirement spec: (1) polished
custom frontend, (2) secure Django login, (3) "Continue with Google" via
django-allauth, (4) product management through customized Django Admin.

**Stack:** Django 6.1.1 · django-allauth 65.19.3 · Pillow · python-dotenv ·
SQLite. Venv at `.venv/` (Windows Git Bash).

**Key files:**
- `config/settings.py` — security hardening, PBKDF2, allauth+Google (creds from `.env`)
- `accounts/` — email-first custom User, login/signup/logout, allauth adapters
- `store/` — Category/Product/ProductImage/Order models, session cart, checkout
- `support/` — tickets + rule-based chatbot (`bot.py`, CSRF-protected JSON API)
- `templates/` + `static/css/main.css` — design system (creme `#8b6f47`/amber
  `#e8a13a` on ivory, Fraunces + Inter), fully responsive
- `store/admin.py` — product admin with multi-image inline (empty gallery
  rows are skipped via `ProductImageForm.clean`)

## Run it

```bash
.venv/Scripts/python manage.py runserver 0.0.0.0:8000   # port 8000 = matches Google OAuth URIs
```

- Site: http://127.0.0.1:8000 · Admin: /admin/
- Customer: `demo@aurora.test` / `DemoPass!2345`
- Admin: `admin@aurora.test` / `AdminPass!2345`
- DB is migrated + seeded (15 handcrafted products, 5 categories (INR prices)). Tests: 28/28 passing.

## Status of the 4 requirements (all verified last session)

1. **Frontend** ✅ — browser-verified via headless Chrome (DOM + screenshots in
   `shots/`, desktop + mobile). All assets 200, 12/12 cards render.
2. **Secure login** ✅ — PBKDF2, generic login errors, min length 10, CSRF
   enforced (tested), POST-only logout, prod hardening when DJANGO_DEBUG=0.
3. **Google OAuth** ⚠️ **one step left** — see below.
4. **Admin product management** ✅ — CRUD + multi-image inline verified via
   real admin POSTs; customers (is_staff=False) blocked (tested).

## ⚠️ Pending: Google OAuth client secret

`.env` has the real client ID but the secret is still `PASTE-YOUR-SECRET-HERE`.
- Fix: Cloud Console → Credentials → OAuth client → **Reset secret** if the
  original is lost → paste into `.env` → restart server.
- Console config: origins `http://127.0.0.1:8000` + `http://localhost:8000`;
  redirect URIs `http://127.0.0.1:8000/accounts/google/login/callback/` (+
  localhost variant). Consent screen in "Testing" mode → add Gmail as Test user.
- **Do NOT also create a SocialApp row in Django admin** — creds live in
  `.env` only, or allauth raises MultipleObjectsReturned.
- A test (`accounts.tests.GoogleOAuthConfigTests`) proves the authorize
  redirect carries the real client ID; full-flow verification is pending the
  secret. (An in-process callback simulation was mid-run last session and had
  a bug in its own mock — `parse_token` lambda missing the adapter arg — not
  a product bug. Re-run with that fixed, or just click the button in a real
  browser once the secret is in.)

## Good next tasks

- [ ] Paste secret → verify full Google login in browser
- [ ] Stripe test-mode checkout (checkout currently records orders, charges nothing)
- [ ] Email verification once SMTP exists (`ACCOUNT_EMAIL_VERIFICATION="none"` today)
- [ ] Production deploy checklist (env vars: DJANGO_SECRET_KEY, DJANGO_DEBUG=0,
      DJANGO_ALLOWED_HOSTS; pip install -r requirements.txt)
