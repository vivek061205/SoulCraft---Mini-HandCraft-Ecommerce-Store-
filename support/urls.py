from django.urls import path

from . import views

app_name = "support"

urlpatterns = [
    path("", views.support_home, name="home"),
    path("chat/", views.chat_api, name="chat"),
    path("ticket/", views.ticket_create, name="ticket"),
]
