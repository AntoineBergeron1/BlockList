from django.contrib import admin

from .models import Category, IPAddress, IPRange, Report, User


# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("nom", "description")


class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "is_staff", "is_active")
    list_editable = ("is_staff", "is_active")


class IPAddressAdmin(admin.ModelAdmin):
    list_display = ("address", "version", "reputation_score", "created_at")
    list_filter = ("version", "reputation_score")
    search_fields = ("address",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


class ReportAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "user", "reason", "created_at")
    list_filter = ("reason", "created_at")
    search_fields = ("ip_address__address", "user__username", "comment")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)


class IPRangeAdmin(admin.ModelAdmin):
    list_display = ("network", "description", "is_blocked", "severity", "created_at")
    list_filter = ("is_blocked", "severity", "created_at")
    search_fields = ("network", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UtilisateurAdmin)
admin.site.register(IPAddress, IPAddressAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(IPRange, IPRangeAdmin)
