from django.shortcuts import render, get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

from accounts.permissions import IsAdminOrReadOnly


# =========================
# CATEGORY LIST
# =========================

@api_view(["GET", "POST"])
@permission_classes([IsAdminOrReadOnly])
def category_list(request):

    if request.method == "GET":

        categories = Category.objects.all()

        serializer = CategorySerializer(
            categories,
            many=True
        )

        return Response(
            serializer.data
        )

    serializer = CategorySerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================
# CATEGORY DETAIL
# =========================

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
def category_detail(request, pk):

    category = get_object_or_404(
        Category,
        pk=pk
    )

    if request.method == "GET":

        serializer = CategorySerializer(
            category
        )

        return Response(
            serializer.data
        )

    if request.method == "PUT":

        serializer = CategorySerializer(
            category,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    category.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


# =========================
# PRODUCT LIST
# =========================

@api_view(["GET", "POST"])
@permission_classes([IsAdminOrReadOnly])
def product_list(request):

    if request.method == "GET":

        products = Product.objects.select_related(
            "category"
        ).all()

        serializer = ProductSerializer(
            products,
            many=True
        )

        return Response(
            serializer.data
        )

    serializer = ProductSerializer(
        data=request.data
    )

    if serializer.is_valid():

        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# =========================
# PRODUCT DETAIL
# =========================

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAdminOrReadOnly])
def product_detail(request, pk):

    product = get_object_or_404(
        Product.objects.select_related(
            "category"
        ),
        pk=pk
    )

    if request.method == "GET":

        serializer = ProductSerializer(
            product
        )

        return Response(
            serializer.data
        )

    if request.method == "PUT":

        serializer = ProductSerializer(
            product,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    product.delete()

    return Response(
        status=status.HTTP_204_NO_CONTENT
    )


# =========================
# PRODUCT LIST PAGE
# =========================

def product_list_page(request):

    products = Product.objects.select_related(
        "category"
    ).filter(
        is_available=True
    )

    return render(
        request,
        "products/product_list.html",
        {
            "products": products
        }
    )


# =========================
# PRODUCT DETAIL PAGE
# =========================

def product_detail_page(request, pk):

    product = get_object_or_404(
        Product.objects.select_related(
            "category"
        ),
        pk=pk
    )

    return render(
        request,
        "products/product_detail.html",
        {
            "product": product
        }
    )