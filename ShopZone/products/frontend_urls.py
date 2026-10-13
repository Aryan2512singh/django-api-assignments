from django.urls import path
from .views import (product_list_page,product_detail_page,)

urlpatterns = [
    path("",product_list_page,name="product-list-page"),
    path("product/<int:pk>/",product_detail_page,name="product-detail-page"),
]