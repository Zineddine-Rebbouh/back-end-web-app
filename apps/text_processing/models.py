# apps/text_processing/models.py
from django.db import models
from django.db.models import JSONField  # Updated import
from apps.data_collection.models import RawData
from django.utils import timezone

class ProcessedData(models.Model):
    raw_data = models.OneToOneField(RawData, on_delete=models.CASCADE, related_name='processed')
    clean_text = models.TextField(help_text="Text after cleaning")
    normalized_text = models.TextField(help_text="Normalized Arabic text")
    tokens = models.JSONField(default=list, blank=True, help_text="Tokenized words")  # Updated (assuming ArrayField, adjust if needed)
    word_count = models.IntegerField(default=0)
    char_count = models.IntegerField(default=0)
    language_confidence = models.FloatField(default=0.0)
    language_metrics = JSONField(default=dict)  # Updated
    processing_metadata = JSONField(default=dict)  # Updated
    processed_at = models.DateTimeField(auto_now_add=True)
    is_analyzed_for_entities = models.BooleanField(default=False)
    is_analyzed_for_sentiment = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['processed_at']),
            models.Index(fields=['is_analyzed_for_entities']),
            models.Index(fields=['is_analyzed_for_sentiment']),
            models.Index(fields=['raw_data']),
        ]
    
    def __str__(self):
        return f"Processed: {self.clean_text[:50]}..."

    def save(self, *args, **kwargs):
        if not self.word_count or not self.char_count:
            self.word_count = len(self.tokens) if self.tokens else 0
            self.char_count = len(self.clean_text) if self.clean_text else 0
        super().save(*args, **kwargs)