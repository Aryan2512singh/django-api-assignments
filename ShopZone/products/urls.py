from django.urls import path

from .views import (category_list,category_detail,product_list,product_detail,)


urlpatterns = [
    # Category API
    path("categories/",category_list,name="category-list"),
    path("categories/<int:pk>/",category_detail,name="category-detail"),
    # Product API
    path("",product_list,name="product-list"),
    path("<int:pk>/",product_detail,name="product-detail"),
]