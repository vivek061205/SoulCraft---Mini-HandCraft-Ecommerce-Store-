"""
Authentication views (Requirement 2).

- Login/signup use Django's authentication system: authenticate() + login().
- Sessions are handled by Django's session framework (db-backed, HttpOnly).
- CSRF is enforced by middleware; every POST template includes {% csrf_token %}.
"""

from django.contrib.auth import login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignupForm


def login_view(request):
    """Email + password sign-in with generic error messages."""
    if request.user.is_authenticated:
        return redirect("store:dashboard")

    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        # Django's built-in auth: creates the authenticated session.
        login(request, form.get_user(), backend="django.contrib.auth.backends.ModelBackend")
        return redirect(request.GET.get("next") or "store:dashboard")

    return render(
        request,
        "registration/login.html",
        {"form": form, "social_login_page": True},
    )


def signup_view(request):
    """Customer registration (regular users; is_staff stays False)."""
    if request.user.is_authenticated:
        return redirect("store:dashboard")

    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("store:dashboard")

    return render(
        request,
        "registration/signup.html",
        {"form": form, "social_login_page": True},
    )


@require_POST  # logout must never be a GET (CSRF-safe, avoids prefetch logout)
def logout_view(request):
    """End the session via Django's logout()."""
    auth_logout(request)
    return redirect("store:dashboard")


@login_required
def profile_view(request):
    return render(request, "registration/profile.html", {"user": request.user})
