# apps/text_processing/api/serializers.py
from rest_framework import serializers
from ..models import ProcessedData

class ProcessedDataSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProcessedData model.
    """
    class Meta:
        model = ProcessedData
        fields = ['id', 'clean_text', 'normalized_text', 'tokens', 'processed_at']