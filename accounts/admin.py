from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, ProfileType, Permission

class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'phone_number', 'is_staff', 'is_active']
    search_fields = ['email', 'phone_number']
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("phone_number",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone_number", "password1", "password2"),
        }),
    )

class ProfileTypeAdmin(admin.ModelAdmin):
    list_display = ["type"]
    search_fields = ["type"]
    filter_horizontal = ("permissions",) 

admin.site.register(User, UserAdmin)
admin.site.register(UserProfile)
admin.site.register(ProfileType, ProfileTypeAdmin)
admin.site.register(Permission)
