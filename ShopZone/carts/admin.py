from django.contrib import admin

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):

    model = CartItem

    extra = 0

    readonly_fields = (
        "product",
        "added_at",
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at",
        "cart_total",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    ordering = (
        "-updated_at",
    )

    inlines = [
        CartItemInline,
    ]

    def cart_total(self, obj):

        return obj.total_price

    cart_total.short_description = "Total"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "cart",
        "product",
        "quantity",
        "item_total",
        "added_at",
    )

    list_filter = (
        "product",
        "added_at",
    )

    search_fields = (
        "cart__user__username",
        "cart__user__email",
        "product__name",
    )

    def item_total(self, obj):

        return obj.total_price

    item_total.short_description = "Total"