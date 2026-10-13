
from django.shortcuts import get_object_or_404, render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsVerifiedUser
from products.models import Product
from .models import Cart, CartItem


def get_user_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

def cart_page(request):
    return render(request, "cart/cart.html")


@api_view(["GET"])
@permission_classes([IsVerifiedUser])
def cart_detail(request):
    cart = get_user_cart(request.user)
    items = cart.items.select_related("product").all()

    return Response({
        "cart_id": cart.id,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "total_price": item.total_price,
            }
            for item in items
        ],
        "total_price": cart.total_price,
    })


@api_view(["POST"])
@permission_classes([IsVerifiedUser])
def add_to_cart(request):
    product_id = request.data.get("product_id")
    raw_quantity = request.data.get("quantity", 1)

    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        return Response(
            {"error": "Quantity must be a positive whole number."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity < 1:
        return Response(
            {"error": "Quantity must be at least 1."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True,
    )

    if product.stock < 1:
        return Response(
            {"error": "This product is currently out of stock."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart = get_user_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )

    new_quantity = quantity if created else cart_item.quantity + quantity

    if new_quantity > product.stock:
        if created:
            cart_item.delete()

        return Response(
            {"error": f"Only {product.stock} item(s) are currently available."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not created:
        cart_item.quantity = new_quantity
        cart_item.save(update_fields=["quantity"])

    return Response(
        {
            "message": "Product added to cart.",
            "product_id": product.id,
            "quantity": cart_item.quantity,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["PUT"])
@permission_classes([IsVerifiedUser])
def update_cart_item(request, item_id):
    raw_quantity = request.data.get("quantity")

    try:
        quantity = int(raw_quantity)
    except (TypeError, ValueError):
        return Response(
            {"error": "Quantity must be a positive whole number."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if quantity < 1:
        return Response(
            {"error": "Quantity must be at least 1."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cart = get_user_cart(request.user)

    item = get_object_or_404(
        CartItem.objects.select_related("product"),
        pk=item_id,
        cart=cart,
    )

    if quantity > item.product.stock:
        return Response(
            {
                "error": (
                    f"Only {item.product.stock} item(s) "
                    "are currently available."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    item.quantity = quantity
    item.save(update_fields=["quantity"])

    return Response({
        "message": "Cart quantity updated.",
        "quantity": item.quantity,
        "total_price": item.total_price,
    })


@api_view(["DELETE"])
@permission_classes([IsVerifiedUser])
def remove_from_cart(request, item_id):
    cart = get_user_cart(request.user)

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart,
    )
    item.delete()

    # HTTP 204 responses must not contain a response body.
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["DELETE"])
@permission_classes([IsVerifiedUser])
def clear_cart(request):
    cart = get_user_cart(request.user)
    cart.items.all().delete()

    return Response(
        {"message": "Cart cleared successfully."},
        status=status.HTTP_200_OK,
    )
