from rest_framework import serializers
from ..models import Topic, Trend, AnalyticsResult

class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'keywords', 'description', 'main_entities', 'creation_date']

class TrendSerializer(serializers.ModelSerializer):
    topic_name = serializers.CharField(source='topic.name')
    class Meta:
        model = Trend
        fields = ['id', 'name', 'description', 'trend_metrics', 'sentiment_distribution', 'status', 'detection_time', 'topic_name']

class AnalyticsResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsResult
        fields = ['id', 'analysis_type', 'time_period_start', 'time_period_end', 'data_points', 'insights']