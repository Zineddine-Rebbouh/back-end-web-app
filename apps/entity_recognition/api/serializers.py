from rest_framework import serializers
from ..models import ExtractedEntity, EntityCatalog

class ExtractedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedEntity
        fields = ['id', 'text', 'normalized', 'entity_type', 'confidence', 'extracted_at']

class EntityCatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityCatalog
        fields = ['entity_id', 'name', 'normalized_name', 'type', 'sport']