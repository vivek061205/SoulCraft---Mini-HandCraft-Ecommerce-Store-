from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # NOTE: canonical routes live in config/urls.py (accounts/login, etc.).
    # This app-level route list is kept intentionally minimal so the names
    # "login"/"signup"/"logout" resolve consistently from templates.
]
