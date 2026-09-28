from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["-date_joined"]
    list_display = ["email", "full_name", "role", "city", "district", "is_verified", "is_active", "date_joined"]
    list_filter = ["role", "is_verified", "is_active", "is_staff", "city"]
    search_fields = ["email", "full_name", "phone_number", "district"]
    readonly_fields = ["date_joined", "last_login"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("المعلومات", {"fields": ["full_name", "phone_number", "profile_image", "governorate", "city", "district"]}),
        ("الصلاحيات", {"fields": ["role", "is_verified", "is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("التواريخ", {"fields": ["date_joined", "last_login"]}),
    ]
    add_fieldsets = [(None, {"classes": ["wide"], "fields": ["email", "full_name", "role", "password1", "password2"]})]
