# apps/entity_recognition/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtractedEntityViewSet, EntityCatalogViewSet

router = DefaultRouter()
router.register(r'extracted', ExtractedEntityViewSet)
router.register(r'catalog', EntityCatalogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]