
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django administration
    path("admin/", admin.site.urls),

    # Backend APIs
    path("api/auth/", include("accounts.urls")),
    path("api/products/", include("products.urls")),
    path("api/cart/", include("carts.urls")),
    path("api/orders/", include("orders.urls")),

    # Frontend pages
    path("cart/", include("carts.frontend_urls")),
    path("orders/", include("orders.frontend_urls")),
    path("", include("products.frontend_urls")),
    path("", include("accounts.frontend_urls")),
]

# Serve uploaded product images during local development only.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
