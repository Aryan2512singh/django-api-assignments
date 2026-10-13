from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "short_description")
    search_fields = ("name", "description")
    ordering = ("name",)
    list_per_page = 20

    @admin.display(description="Description")
    def short_description(self, obj):
        if not obj.description:
            return "—"
        return (
            obj.description[:65] + "..."
            if len(obj.description) > 65
            else obj.description
        )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "category",
        "price",
        "stock",
        "is_available",
        "image_preview",
        "created_at",
    )

    list_filter = (
        "category",
        "is_available",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "category__name",
    )

    list_editable = (
        "price",
        "stock",
        "is_available",
    )

    autocomplete_fields = ("category",)

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )

    fieldsets = (
        (
            "Product Information",
            {
                "fields": (
                    "name",
                    "category",
                    "description",
                )
            },
        ),
        (
            "Pricing and Inventory",
            {
                "fields": (
                    "price",
                    "stock",
                    "is_available",
                )
            },
        ),
        (
            "Product Image",
            {
                "fields": (
                    "image",
                    "image_preview",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    ordering = ("-created_at",)
    list_per_page = 25

    @admin.display(description="Image")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" width="55" height="55" '
                'style="object-fit:contain;border-radius:8px;" />',
                obj.image.url,
            )
        return "No image"