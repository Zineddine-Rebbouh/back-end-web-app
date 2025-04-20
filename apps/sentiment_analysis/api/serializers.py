from rest_framework import serializers
from ..models import SentimentAnalysis, EntitySentiment

class SentimentAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentimentAnalysis
        fields = ['id', 'label', 'score', 'confidence', 'analyzed_at']

class EntitySentimentSerializer(serializers.ModelSerializer):
    entity_text = serializers.CharField(source='entity.text')
    class Meta:
        model = EntitySentiment
        fields = ['id', 'entity_text', 'label', 'score', 'confidence']