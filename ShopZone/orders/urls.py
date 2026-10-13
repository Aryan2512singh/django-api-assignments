
from django.urls import path

from .views import create_order, my_orders, order_detail

urlpatterns = [
    path("", my_orders, name="my-orders"),
    path("create/", create_order, name="create-order"),
    path("<int:order_id>/", order_detail, name="order-detail"),
]
