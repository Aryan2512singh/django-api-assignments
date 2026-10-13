from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "product",
        "product_name",
        "price",
        "quantity",
        "total_price",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "full_name",
        "phone",
        "total_amount",
        "payment_method",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "payment_method",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone",
        "pincode",
    )

    readonly_fields = (
        "user",
        "total_amount",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )

    inlines = [
        OrderItemInline,
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "product_name",
        "price",
        "quantity",
        "total_price",
    )

    search_fields = (
        "product_name",
        "order__user__username",
        "order__user__email",
    )