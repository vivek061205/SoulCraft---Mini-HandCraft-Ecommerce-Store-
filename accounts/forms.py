"""
Authentication forms.

Security notes:
- Minimum password length (10) enforced here AND by the AUTH_PASSWORD_VALIDATORS.
- Wrong credentials return one generic message: we never reveal whether the
  email or the password was incorrect.
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import User

GENERIC_LOGIN_ERROR = (
    "Invalid email or password. Please try again or reset your password."
)


class SignupForm(UserCreationForm):
    """Customer registration: name, email, password (validated)."""

    name = forms.CharField(
        max_length=150,
        label="Full name",
        widget=forms.TextInput(
            attrs={"placeholder": "Ada Lovelace", "autocomplete": "name"}
        ),
    )
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={"placeholder": "you@example.com", "autocomplete": "email"}
        ),
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "At least 10 characters",
                "autocomplete": "new-password",
            }
        ),
        help_text="Use at least 10 characters. Avoid common passwords.",
    )

    class Meta:
        model = User
        fields = ("name", "email", "password1")
        widgets = {"password2": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We intentionally do not ask users to repeat the password twice; the
        # UserCreationForm parent expects password2, so neutralize it.
        self.fields.pop("password2", None)

    def clean_email(self):
        email = self.cleaned_data["email"].lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            # Do not confirm or deny which field failed on login; signup can
            # be explicit because it is a *registration*, not an auth check.
            raise forms.ValidationError(
                "An account with this email already exists. Try signing in instead."
            )
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1") or ""
        if len(password) < 10:
            raise forms.ValidationError("Passwords must be at least 10 characters long.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        names = self.cleaned_data["name"].split(" ", 1)
        user.first_name = names[0]
        if len(names) > 1:
            user.last_name = names[1]
        user.email = self.cleaned_data["email"].lower().strip()
        user.is_staff = False  # regular customers never get admin access
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Email + password sign-in using Django's authenticate()/login()."""

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={"placeholder": "you@example.com", "autocomplete": "email"}
        ),
    )
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Your password", "autocomplete": "current-password"}
        ),
    )

    error_messages = {"invalid_login": GENERIC_LOGIN_ERROR}

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email", "").lower().strip()
        password = cleaned.get("password") or ""

        if email and password:
            # Django's ModelBackend + custom User (USERNAME_FIELD=email).
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                # Same message whether the email OR the password was wrong.
                raise forms.ValidationError(GENERIC_LOGIN_ERROR)
            elif not self.user_cache.is_active:
                raise forms.ValidationError(GENERIC_LOGIN_ERROR)
            self.cleaned_data["user"] = self.user_cache
        return cleaned

    def get_user(self):
        return getattr(self, "user_cache", None)
