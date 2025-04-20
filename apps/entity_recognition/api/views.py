# apps/entity_recognition/api/views.py
from rest_framework import viewsets
from ..models import ExtractedEntity, EntityCatalog
from .serializers import ExtractedEntitySerializer, EntityCatalogSerializer

class ExtractedEntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing extracted entities.
    """
    queryset = ExtractedEntity.objects.all().order_by('-extracted_at')
    serializer_class = ExtractedEntitySerializer

class EntityCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing the entity catalog.
    """
    queryset = EntityCatalog.objects.all().order_by('-last_updated')
    serializer_class = EntityCatalogSerializer