# apps/trend_analysis/models.py
from django.db import models
from django.db.models import JSONField  # Updated import
from apps.entity_recognition.models import EntityCatalog
from apps.data_collection.models import RawData
from django.utils import timezone

class Topic(models.Model):
    name = models.CharField(max_length=255)
    keywords = models.JSONField(default=list)  # Updated (assuming ArrayField, adjust if needed)
    description = models.TextField()
    main_entities = JSONField()  # Updated
    related_topics = JSONField(default=list, blank=True)  # Updated
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    metadata = JSONField(default=dict)  # Updated
    
    class Meta:
        indexes = [
            models.Index(fields=['creation_date']),
            models.Index(fields=['status']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name

class Trend(models.Model):
    TREND_STATUS = (
        ('emerging', 'Emerging'),
        ('peaking', 'Peaking'),
        ('declining', 'Declining'),
        ('ended', 'Ended'),
    )
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='trends')
    name = models.CharField(max_length=255)
    description = models.TextField()
    trend_metrics = JSONField()  # Updated
    sentiment_distribution = JSONField()  # Updated
    geographical_distribution = JSONField(default=list)  # Updated
    influential_sources = JSONField(default=list)  # Updated
    sample_content = models.ManyToManyField(RawData, related_name='featured_in_trends')
    detection_time = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=TREND_STATUS, default='emerging')
    
    class Meta:
        indexes = [
            models.Index(fields=['detection_time']),
            models.Index(fields=['status']),
            models.Index(fields=['topic']),
        ]
    
    def __str__(self):
        return self.name

class AnalyticsResult(models.Model):
    ANALYSIS_TYPES = (
        ('volume', 'Tweet Volume'),
        ('sentiment', 'Sentiment Distribution'),
        ('entity', 'Entity Trends'),
    )
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    entity = models.ForeignKey(EntityCatalog, on_delete=models.SET_NULL, null=True, blank=True, related_name='analytics')
    time_period_start = models.DateTimeField()
    time_period_end = models.DateTimeField()
    data_points = JSONField()  # Updated
    insights = JSONField(default=list)  # Updated
    related_trends = JSONField(default=list)  # Updated
    metadata = JSONField(default=dict)  # Updated
    created_at = models.DateTimeField(auto_now_add=True)
    analysis_version = models.CharField(max_length=50, default="v1")
    
    class Meta:
        indexes = [
            models.Index(fields=['analysis_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['entity']),
        ]
    
    def __str__(self):
        return f"{self.get_analysis_type_display()} {self.time_period_start.date()} - {self.time_period_end.date()}"