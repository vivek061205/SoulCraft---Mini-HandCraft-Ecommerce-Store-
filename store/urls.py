from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("buy-now/<int:product_id>/", views.buy_now, name="buy_now"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout_view, name="checkout"),
]
