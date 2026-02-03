from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ------------------------
    # Admin
    # ------------------------
    path("admin/", admin.site.urls),

    # ------------------------
    # OpenAPI / API Documentation
    # ------------------------
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/v1/docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # ------------------------
    # App Endpoints
    # ------------------------
    path("api/v1/accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    # ------------------------
    # Health Check
    # ------------------------
    path("api/v1/health/", include(("health.urls", "health"), namespace="health")),
]

# ------------------------
# Serve media files in development
# ------------------------
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
