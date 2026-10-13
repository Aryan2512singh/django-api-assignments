
from django.db import transaction
from django.shortcuts import get_object_or_404, render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from accounts.permissions import IsVerifiedUser
from carts.models import Cart
from products.models import Product
from .models import Order, OrderItem


def checkout_page(request):
    return render(request, "orders/checkout.html")


def orders_page(request):
    return render(request, "orders/orders.html")


def serialize_order(order):
    return {
        "id": order.id,
        "created_at": order.created_at,
        "status": order.status,
        "total_amount": order.total_amount,
        "payment_method": order.payment_method,
        "full_name": order.full_name,
        "phone": order.phone,
        "address": order.address,
        "city": order.city,
        "state": order.state,
        "pincode": order.pincode,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "price": item.price,
                "quantity": item.quantity,
                "total_price": item.total_price,
            }
            for item in order.items.all()
        ],
    }


@api_view(["POST"])
@permission_classes([IsVerifiedUser])
def create_order(request):
    required_fields = (
        "full_name",
        "phone",
        "address",
        "city",
        "state",
        "pincode",
    )

    values = {
        field: str(request.data.get(field, "")).strip()
        for field in required_fields
    }

    missing_fields = [
        field for field, value in values.items() if not value
    ]

    if missing_fields:
        return Response(
            {
                "error": "Please complete all required delivery fields.",
                "fields": missing_fields,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    payment_method = str(
        request.data.get("payment_method", "cod")
    ).strip().lower()

    if payment_method not in {"cod", "online"}:
        return Response(
            {"error": "Unsupported payment method."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Never accept an online order as paid without a real payment gateway.
    if payment_method == "online":
        return Response(
            {
                "error": (
                    "Online payments are not configured yet. "
                    "Please choose Cash on Delivery."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        with transaction.atomic():
            cart = (
                Cart.objects
                .select_for_update()
                .get(user=request.user)
            )

            cart_items = list(
                cart.items.select_related("product").all()
            )

            if not cart_items:
                return Response(
                    {"error": "Your cart is empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Re-fetch products and validate current stock inside the
            # transaction instead of trusting data from the browser.
            checked_items = []
            total_amount = 0

            for cart_item in cart_items:
                product = get_object_or_404(
                    Product.objects.select_for_update(),
                    pk=cart_item.product_id,
                )

                if not product.is_available or product.stock < 1:
                    return Response(
                        {
                            "error": (
                                f"{product.name} is no longer available."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if cart_item.quantity > product.stock:
                    return Response(
                        {
                            "error": (
                                f"Only {product.stock} unit(s) of "
                                f"{product.name} are available."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                line_total = product.price * cart_item.quantity
                total_amount += line_total

                checked_items.append(
                    (cart_item, product, line_total)
                )

            order = Order.objects.create(
                user=request.user,
                full_name=values["full_name"],
                phone=values["phone"],
                address=values["address"],
                city=values["city"],
                state=values["state"],
                pincode=values["pincode"],
                payment_method="cod",
                total_amount=total_amount,
            )

            for cart_item, product, line_total in checked_items:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    price=product.price,
                    quantity=cart_item.quantity,
                    total_price=line_total,
                )

                product.stock -= cart_item.quantity

                if product.stock == 0:
                    product.is_available = False
                    product.save(
                        update_fields=["stock", "is_available"]
                    )
                else:
                    product.save(update_fields=["stock"])

            cart.items.all().delete()

    except Cart.DoesNotExist:
        return Response(
            {"error": "Your cart is empty."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": "Order placed successfully.",
            "order": serialize_order(order),
            "order_id": order.id,
            "total_amount": order.total_amount,
            "status": order.status,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsVerifiedUser])
def my_orders(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at", "-id")
    )

    return Response([
        serialize_order(order) for order in orders
    ])


@api_view(["GET"])
@permission_classes([IsVerifiedUser])
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
        user=request.user,
    )

    return Response(serialize_order(order))
