from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScanViewSet, ReportViewSet

router = DefaultRouter()
router.register(r'scans', ScanViewSet, basename='scan')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
