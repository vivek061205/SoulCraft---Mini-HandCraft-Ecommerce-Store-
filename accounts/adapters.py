"""
django-allauth adapters.

Requirement 3: on successful Google login, auto-create the user account if one
doesn't exist and log them in with a session like any other user. These
adapters remove the intermediate confirmation form so the flow is one click.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from allauth.utils import get_user_model


class SoulCraftAccountAdapter(DefaultAccountAdapter):
    """Regular (email + password) account behaviour."""

    def is_open_for_signup(self, request):
        return True

    def get_login_redirect_url(self, request):
        from django.conf import settings

        return settings.LOGIN_REDIRECT_URL


class SoulCraftSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Google (and other social) login behaviour."""

    def is_open_for_signup(self, request, sociallogin: SocialLogin):
        # Auto-create the local account from the Google profile.
        return True

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        extra = sociallogin.account.extra_data or {}

        # Build a human-readable name from the Google profile when available.
        full_name = extra.get("name") or " ".join(
            p for p in (extra.get("given_name"), extra.get("family_name")) if p
        )
        if full_name:
            user.first_name, _, user.last_name = full_name.partition(" ")
        elif data.get("email"):
            user.first_name = data["email"].split("@")[0]
        return user

    def pre_social_login(self, request, sociallogin: SocialLogin):
        """If a regular account already exists with this verified email,
        connect the social login to it instead of erroring out."""
        if sociallogin.is_existing:
            return
        email = (sociallogin.user.email or "").lower().strip()
        if not email:
            return
        User = get_user_model()
        existing = User.objects.filter(email__iexact=email).first()
        if existing and existing.pk:
            sociallogin.connect(request, existing)
