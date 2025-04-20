# apps/sentiment_analysis/models.py
from django.db import models
from django.db.models import JSONField
from apps.text_processing.models import ProcessedData
from apps.data_collection.models import RawData
from apps.entity_recognition.models import ExtractedEntity

class SentimentAnalysis(models.Model):
    SENTIMENT_LABELS = (
        ('POSITIVE', 'Positive'),
        ('NEUTRAL', 'Neutral'),
        ('NEGATIVE', 'Negative'),
    )
    
    processed_data = models.OneToOneField(ProcessedData, on_delete=models.CASCADE, related_name='sentiment')
    raw_data = models.OneToOneField(RawData, on_delete=models.CASCADE, related_name='sentiment')
    label = models.CharField(max_length=20, choices=SENTIMENT_LABELS)
    score = models.FloatField()
    confidence = models.FloatField()
    emotion_analysis = JSONField(default=dict)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50, default="arabert_v1")
    
    class Meta:
        indexes = [
            models.Index(fields=['label']),
            models.Index(fields=['analyzed_at']),
            models.Index(fields=['processed_data']),
        ]
    
    def __str__(self):
        return f"Sentiment: {self.get_label_display()} (Score: {self.score:.2f}, Confidence: {self.confidence:.2f})"

class EntitySentiment(models.Model):
    SENTIMENT_LABELS = (
        ('POSITIVE', 'Positive'),
        ('NEUTRAL', 'Neutral'),
        ('NEGATIVE', 'Negative'),
    )
    
    sentiment_analysis = models.ForeignKey(SentimentAnalysis, on_delete=models.CASCADE, related_name='entity_sentiments')
    entity = models.ForeignKey(ExtractedEntity, on_delete=models.CASCADE, related_name='sentiments')
    label = models.CharField(max_length=20, choices=SENTIMENT_LABELS)
    score = models.FloatField()
    confidence = models.FloatField()
    aspect_sentiments = JSONField(default=list, blank=True)
    
    class Meta:
        unique_together = ('sentiment_analysis', 'entity')
        indexes = [
            models.Index(fields=['label']),
            models.Index(fields=['entity']),
        ]
    
    def __str__(self):
        return f"{self.entity.text}: {self.get_label_display()} (Score: {self.score:.2f})"