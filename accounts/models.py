"""
Custom user model: email is the identity, no username.

Password storage is untouched -- Django's built-in PBKDF2 hasher does the
hashing/verification (see config/settings.py PASSWORD_HASHERS).
"""

from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    """Email-first manager: username is derived automatically in User.save()."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)  # hashed by Django's password hashers
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Email-first user. `username` is kept for admin convenience but is
    auto-derived from the email; customers log in with email + password."""

    objects = UserManager()

    email = models.EmailField("email address", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"

    def save(self, *args, **kwargs):
        if not self.username:
            # Derive a unique, admin-friendly username from the email.
            base = (self.email.split("@")[0] or "user")[:140]
            candidate, suffix = base, 1
            while (
                type(self).objects.filter(username=candidate)
                .exclude(pk=self.pk)
                .exists()
            ):
                suffix += 1
                candidate = f"{base}_{suffix}"
            self.username = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
