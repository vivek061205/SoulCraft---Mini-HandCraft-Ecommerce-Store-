from django.contrib import admin

from .models import SupportTicket


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "email", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("subject", "message", "email")
    readonly_fields = ("email", "subject", "message", "user", "created_at")
    list_editable = ("status",)
