

from django.urls import path
from .views import cart_page

urlpatterns = [
    path("", cart_page, name="cart-page"),
]
