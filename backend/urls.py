from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenBlacklistView
from rest_framework.routers import DefaultRouter
from apps.users.views import CustomUserViewSet

router = DefaultRouter()
router.register("users", CustomUserViewSet)


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api/auth/", include("djoser.urls")),
    path("api/auth/", include(router.urls)),
    path("api/auth/", include("djoser.urls.jwt")),
    path("api/radiology/", include("apps.radiology.urls")),
    path("api/auth/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)