from django.contrib import admin
from .models import Category, User

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("nom", "description")

class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "is_staff", "is_active")
    list_editable = ("is_staff","is_active")


admin.site.register(Category, CategoryAdmin)
admin.site.register(User, UtilisateurAdmin)