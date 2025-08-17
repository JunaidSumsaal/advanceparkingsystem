from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp", "ip_address")
    list_filter = ("action", "timestamp")
    search_fields = ("user__username", "description", "ip_address")
