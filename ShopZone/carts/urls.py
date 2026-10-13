from django.urls import path

from .views import (
    cart_detail,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
)


urlpatterns = [

    path(
        "",
        cart_detail,
        name="cart-detail"
    ),

    path(
        "add/",
        add_to_cart,
        name="add-to-cart"
    ),

    path(
        "item/<int:item_id>/",
        update_cart_item,
        name="update-cart-item"
    ),

    path(
        "item/<int:item_id>/remove/",
        remove_from_cart,
        name="remove-from-cart"
    ),

    path(
        "clear/",
        clear_cart,
        name="clear-cart"
    ),

]