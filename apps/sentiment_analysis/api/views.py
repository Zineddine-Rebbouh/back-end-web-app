# apps/sentiment_analysis/api/views.py
from rest_framework import viewsets
from ..models import SentimentAnalysis, EntitySentiment
from .serializers import SentimentAnalysisSerializer, EntitySentimentSerializer

class SentimentAnalysisViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing document-level sentiment analysis.
    """
    queryset = SentimentAnalysis.objects.all().order_by('-analyzed_at')
    serializer_class = SentimentAnalysisSerializer

class EntitySentimentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing entity-level sentiment analysis.
    """
    queryset = EntitySentiment.objects.all().order_by('-sentiment_analysis__analyzed_at')
    serializer_class = EntitySentimentSerializer