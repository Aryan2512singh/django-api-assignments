from django.urls import path

from .views import (
    checkout_page,
    orders_page,
)


urlpatterns = [

    path(
        "",
        orders_page,
        name="orders-page"
    ),

    path(
        "checkout/",
        checkout_page,
        name="checkout-page"
    ),

]

