# apps/trend_analysis/api/views.py
from rest_framework import viewsets
from ..models import Topic, Trend, AnalyticsResult
from .serializers import TopicSerializer, TrendSerializer, AnalyticsResultSerializer

class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing topics.
    """
    queryset = Topic.objects.all().order_by('-creation_date')
    serializer_class = TopicSerializer

class TrendViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing trends.
    """
    queryset = Trend.objects.all().order_by('-detection_time')
    serializer_class = TrendSerializer

class AnalyticsResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for viewing analytics results.
    """
    queryset = AnalyticsResult.objects.all().order_by('-created_at')
    serializer_class = AnalyticsResultSerializer