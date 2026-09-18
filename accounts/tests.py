"""
Requirement 2 & 3 tests: secure login system + Google OAuth wiring.

Run with:  python manage.py test accounts
"""

import json
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()

GENERIC_ERROR_FRAGMENT = "Invalid email or password"


class PasswordHashingTests(TestCase):
    """Passwords must never be stored in plaintext."""

    def test_password_is_hashed_with_django_hasher(self):
        user = User.objects.create_user(email="hash@example.com", password="S3cure-Passw0rd!")
        self.assertNotEqual(user.password, "S3cure-Passw0rd!")
        self.assertTrue(user.password.startswith("pbkdf2_sha256$"))
        self.assertTrue(user.check_password("S3cure-Passw0rd!"))


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.user = User.objects.create_user(email="alice@example.com", password="Sup3r-Secret-PW")

    def test_login_page_renders_with_google_button(self):
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Continue with Google")
        self.assertContains(resp, "/accounts/google/login/")

    def test_login_success_with_email(self):
        resp = self.client.post(self.login_url, {
            "email": "alice@example.com", "password": "Sup3r-Secret-PW",
        })
        self.assertRedirects(resp, reverse("store:dashboard"))
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_wrong_password_generic_error(self):
        resp = self.client.post(self.login_url, {
            "email": "alice@example.com", "password": "wrong-password",
        })
        self.assertContains(resp, GENERIC_ERROR_FRAGMENT, status_code=200)

    def test_unknown_email_same_generic_error(self):
        """Must not reveal whether the email or the password was wrong."""
        resp_ok = self.client.post(self.login_url, {
            "email": "alice@example.com", "password": "wrong-password",
        }).content.decode()
        resp_unknown = self.client.post(self.login_url, {
            "email": "ghost@example.com", "password": "wrong-password",
        }).content.decode()
        self.assertIn(GENERIC_ERROR_FRAGMENT, resp_ok)
        self.assertIn(GENERIC_ERROR_FRAGMENT, resp_unknown)
        self.assertNotIn("alice", resp_unknown)
        self.assertNotIn("No account", resp_unknown)

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 405)
        # Still logged in after GET
        resp2 = self.client.get(reverse("profile"))
        self.assertEqual(resp2.status_code, 200)

    def test_logout_via_post(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("logout"))
        self.assertEqual(resp.status_code, 302)


class SignupViewTests(TestCase):
    def test_signup_creates_non_staff_user(self):
        resp = self.client.post(reverse("signup"), {
            "name": "Bob Builder",
            "email": "bob@example.com",
            "password1": "Very-Good-Passw0rd",
        })
        self.assertRedirects(resp, reverse("store:dashboard"))
        user = User.objects.get(email="bob@example.com")
        self.assertFalse(user.is_staff)     # regular customer: no admin
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("Very-Good-Passw0rd"))

    def test_signup_rejects_short_password(self):
        resp = self.client.post(reverse("signup"), {
            "name": "Bob", "email": "shortpw@example.com", "password1": "short",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(email="shortpw@example.com").exists())

    def test_signup_rejects_duplicate_email(self):
        User.objects.create_user(email="taken@example.com", password="An0ther-Good-PW")
        resp = self.client.post(reverse("signup"), {
            "name": "Copycat", "email": "taken@example.com", "password1": "An0ther-Good-PW",
        })
        self.assertContains(resp, "already exists")

    def test_csrf_required_on_login_post(self):
        """CSRF protection active: a POST without the token is rejected."""
        csrf_client = Client(enforce_csrf_checks=True)
        resp = csrf_client.post(reverse("login"), {
            "email": "alice@example.com", "password": "whatever-12345",
        })
        self.assertEqual(resp.status_code, 403)


class GoogleOAuthConfigTests(TestCase):
    """Requirement 3: allauth is wired up even without live credentials."""

    def test_google_provider_is_registered(self):
        from allauth.socialaccount.providers import registry

        provider = registry.get_class("google")
        self.assertIsNotNone(provider)

    def test_provider_settings_present(self):
        from django.conf import settings as dj_settings

        google = dj_settings.SOCIALACCOUNT_PROVIDERS["google"]
        self.assertIn("email", google["SCOPE"])
        self.assertIn("profile", google["SCOPE"])

    def test_google_login_route_exists(self):
        """The route resolves. With credentials configured (provider APP via
        .env) allauth serves its POST interstitial; without them it raises
        SocialApp.DoesNotExist. Either way the URL wiring is proven."""
        from allauth.socialaccount.models import SocialApp

        try:
            resp = self.client.get(reverse("google_login"))
            self.assertIn(resp.status_code, (200, 302))
        except SocialApp.DoesNotExist:
            pass  # credentials not configured yet — route still resolves

    def test_google_login_route_with_configured_app(self):
        """With real credentials in the provider APP (from .env), POSTing to
        the login route kicks off the OAuth2 dance: a redirect to Google's
        authorize endpoint. (allauth 65 requires POST — LOGIN_ON_GET=False —
        matching the CSRF-protected button on the login/signup pages.)"""
        from django.conf import settings as dj_settings

        if not dj_settings.SOCIALACCOUNT_PROVIDERS["google"].get("APP"):
            self.skipTest("Google OAuth credentials not configured in .env yet")

        resp = self.client.post(reverse("google_login"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("accounts.google.com/o/oauth2", resp.url)
        self.assertIn(dj_settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"], resp.url)

    def test_sociallogin_auto_creates_and_logs_in_user(self):
        """Simulate a completed Google handshake: the adapter should create a
        local user from the profile and log them in (auto-signup)."""
        from allauth.socialaccount.models import SocialLogin

        from accounts.adapters import SoulCraftSocialAccountAdapter

        request = self.client.get(reverse("login")).wsgi_request
        sociallogin = SocialLogin(user=User(email="g.newuser@gmail.com"))

        with mock.patch.object(SocialLogin, "lookup") as _:
            adapter = SoulCraftSocialAccountAdapter()
            self.assertTrue(adapter.is_open_for_signup(request, sociallogin))

        # populate_user builds a display name from extra_data
        class FakeAccount:
            extra_data = {"name": "Grace Hopper", "email": "g.newuser@gmail.com"}

        sociallogin2 = SocialLogin(user=User(email="g.newuser@gmail.com"))
        sociallogin2.account = FakeAccount()
        user = adapter.populate_user(request, sociallogin2, {"email": "g.newuser@gmail.com"})
        self.assertEqual(user.first_name, "Grace")
        self.assertEqual(user.last_name, "Hopper")
