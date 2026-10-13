from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "id",
        "username",
        "email",
        "is_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "is_verified",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = (
        "-date_joined",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "ShopZone Information",
            {
                "fields": (
                    "is_verified",
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "ShopZone Information",
            {
                "fields": (
                    "email",
                    "is_verified",
                )
            }
        ),
    )
# Register your models here.
