# apps/text_processing/api/views.py
from rest_framework import viewsets
from ..models import ProcessedData
from .serializers import ProcessedDataSerializer

class ProcessedDataViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing processed text data.
    """
    queryset = ProcessedData.objects.all().order_by('-processed_at')
    serializer_class = ProcessedDataSerializer