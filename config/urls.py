"""
URL configuration.

/admin/            -> customized Django admin (staff/superuser only)
/accounts/...      -> secure email login, signup, logout (Requirement 2)
/accounts/google/  -> "Continue with Google" via django-allauth (Requirement 3)
/                  -> storefront: dashboard, product detail, cart, checkout
/support/          -> support center + chatbot page and JSON API
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from accounts import views as account_views
admin.site.site_header = "SoulCraft — Product Management"
admin.site.site_title = "SoulCraft Admin"
admin.site.index_title = "Handcrafted catalog administration"

urlpatterns = [
    path("admin/", admin.site.urls),

    # Requirement 2: secure login system
    path("accounts/login/", account_views.login_view, name="login"),
    path("accounts/signup/", account_views.signup_view, name="signup"),
    path("accounts/logout/", account_views.logout_view, name="logout"),
    path("accounts/profile/", account_views.profile_view, name="profile"),

    # Requirement 3: Google OAuth
    path("accounts/", include("allauth.urls")),

    # Storefront
    path("", include("store.urls")),

    # Support + chatbot
    path("support/", include("support.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
