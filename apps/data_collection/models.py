# apps/data_collection/models.py
from django.db import models
from django.db.models import JSONField  # Updated import
from django.utils import timezone

class DataSource(models.Model):
    SOURCE_TYPES = (
        ('youtube', 'Youtube'),
    )
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    is_active = models.BooleanField(default=True)
    api_credentials = JSONField(null=True, blank=True)  # Updated
    collection_rules = JSONField()  # Updated
    schedule_frequency = models.IntegerField(help_text="Frequency in minutes")
    max_items_per_collection = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_collection_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"

class RawData(models.Model):
    source = models.CharField(max_length=20, default='youtube')
    source_id = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    author_id = models.CharField(max_length=255, null=True, blank=True)
    author_name = models.CharField(max_length=255, null=True, blank=True)
    author_followers = models.IntegerField(null=True, blank=True)
    author_verified = models.BooleanField(default=False)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    language = models.CharField(max_length=10, default='ar')
    location = models.CharField(max_length=255, null=True, blank=True)
    coordinates = JSONField(null=True, blank=True)  # Updated
    urls = models.JSONField(default=list, blank=True)  # Updated (assuming this was meant to be ArrayField, adjust if needed)
    hashtags = models.JSONField(default=list, blank=True)  # Updated (assuming ArrayField, adjust if needed)
    mentions = models.JSONField(default=list, blank=True)  # Updated (assuming ArrayField, adjust if needed)
    sport_category = models.JSONField(default=list, blank=True)  # Updated (assuming ArrayField, adjust if needed)
    media = JSONField(default=list, blank=True)  # Updated
    created_at = models.DateTimeField()
    collected_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['source', 'source_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_processed']),
        ]
        unique_together = ('source', 'source_id')
    
    def __str__(self):
        return f"Youtube: {self.content[:50]}..."
    
    
# from django.db import models
# from django.db.models import JSONField
# from django.utils import timezone

# class DataSource(models.Model):
#     SOURCE_TYPES = (
#         ('twitter', 'Twitter'),
#     )
    
#     name = models.CharField(max_length=100)
#     source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
#     is_active = models.BooleanField(default=True)
#     collection_rules = JSONField()  # e.g., {"keywords": ["football", "tennis"]}
#     schedule_frequency = models.IntegerField(help_text="Frequency in minutes")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     def __str__(self):
#         return f"{self.name} ({self.get_source_type_display()})"

# class RawData(models.Model):
#     source = models.CharField(max_length=20, default='twitter')
#     source_id = models.CharField(max_length=255, unique=True)
#     content = models.TextField()
#     author_id = models.CharField(max_length=255, null=True, blank=True)
#     likes = models.IntegerField(default=0)
#     shares = models.IntegerField(default=0)
#     comments = models.IntegerField(default=0)
#     language = models.CharField(max_length=10, default='ar')
#     hashtags = JSONField(default=list, blank=True)  # e.g., ["#FIFA", "#Sports"]
#     mentions = JSONField(default=list, blank=True)  # e.g., ["@user1"]
#     created_at = models.DateTimeField()
#     collected_at = models.DateTimeField(auto_now_add=True)
#     is_processed = models.BooleanField(default=False)
    
#     class Meta:
#         indexes = [
#             models.Index(fields=['source', 'source_id']),
#             models.Index(fields=['created_at']),
#             models.Index(fields=['is_processed']),
#         ]
#         unique_together = ('source', 'source_id')
    
#     def __str__(self):
#         return f"Twitter: {self.content[:50]}..."